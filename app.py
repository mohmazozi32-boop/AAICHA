import streamlit as st
import json
import os
from dataclasses import dataclass

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="DTR Thermal Checker", layout="wide")

DATA_FILES = [
    "data_communes_algeria.json",
    "communes_zone_A.json",
    "communes_zone_B.json",
    "communes_zone_C.json",
    "communes_zone_Inconnue.json",
]

# =========================
# LOAD DATA
# =========================
def load_all_communes():
    all_data = []
    for file in DATA_FILES:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                try:
                    all_data.extend(json.load(f))
                except:
                    pass
    return all_data

communes = load_all_communes()

# =========================
# SIMPLE DTR LOGIC (RULE BASED)
# =========================
def evaluate_building(zone, insulation_type, wall_r, roof_r):
    score = 0

    # Zone influence
    zone_factor = {"A": 1.2, "B": 1.0, "C": 0.8, "Inconnue": 1.0}
    score += zone_factor.get(zone, 1.0)

    # Wall resistance
    if wall_r >= 2.5:
        score += 1.5
    elif wall_r >= 1.5:
        score += 1.0
    else:
        score += 0.3

    # Roof resistance
    if roof_r >= 3:
        score += 1.5
    elif roof_r >= 2:
        score += 1.0
    else:
        score += 0.4

    # insulation type
    if insulation_type == "exterieure":
        score += 1.2
    elif insulation_type == "interieure":
        score += 0.8
    else:
        score += 1.0

    # Decision
    if score >= 4:
        return "✔ العزل سليم (Conforme)", score
    elif score >= 3:
        return "⚠ مقبول لكن يحتاج تحسين", score
    else:
        return "✖ العزل غير سليم", score


# =========================
# UI
# =========================
st.title("🏗️ DTR Thermal Building Checker")
st.write("تحليل العزل الحراري حسب الموقع وخصائص المبنى")

col1, col2 = st.columns(2)

with col1:
    selected_city = st.selectbox(
        "اختر المدينة",
        options=[c["name"] for c in communes] if communes else ["Unknown"]
    )

    insulation_type = st.selectbox(
        "نوع العزل",
        ["repartie", "interieure", "exterieure"]
    )

with col2:
    wall_r = st.number_input("مقاومة الجدار R (m²·K/W)", 0.1, 10.0, 1.5)
    roof_r = st.number_input("مقاومة السقف R (m²·K/W)", 0.1, 10.0, 2.0)

# =========================
# GET CITY DATA
# =========================
city_data = next((c for c in communes if c["name"] == selected_city), None)

if city_data:
    st.info(f"""
    📍 المدينة: {city_data['name_ar']}
    🌡️ المنطقة الشتوية: {city_data.get('thermal_zone_winter', 'N/A')}
    📏 الارتفاع: {city_data.get('elevation', 'N/A')} m
    """)

# =========================
# CHECK BUTTON
# =========================
if st.button("🔍 تحليل العزل"):
    if city_data:
        result, score = evaluate_building(
            city_data.get("thermal_zone_winter", "Inconnue"),
            insulation_type,
            wall_r,
            roof_r
        )

        st.subheader("📊 النتيجة")
        st.write(result)

        st.metric("Score thermique", round(score, 2))

        # Recommendation
        if score < 3:
            st.warning("🔧 توصية: زيادة سماكة العزل أو تحسين نوعه")
        elif score < 4:
            st.info("ℹ️ العزل مقبول لكن يمكن تحسينه")
        else:
            st.success("🏆 أداء حراري جيد")
    else:
        st.error("لم يتم العثور على المدينة")
