import streamlit as st
import json

# المسارات مباشرة بجانب app.py
PATH_COMMUNES = "data_communes_algeria.json"
PATH_MATERIAUX = "dtr_materiaux.json"
PATH_PAROIS = "dtr_parois_enterrees.json"
PATH_PONTS = "dtr_ponts_thermiques.json"

# تحميل البيانات
with open(PATH_COMMUNES, "r", encoding="utf-8") as f:
    communes_data = json.load(f)

with open(PATH_MATERIAUX, "r", encoding="utf-8") as f:
    materiaux_data = json.load(f)

with open(PATH_PAROIS, "r", encoding="utf-8") as f:
    parois_enterrees = json.load(f)

with open(PATH_PONTS, "r", encoding="utf-8") as f:
    ponts_thermiques = json.load(f)

# قاموس الترجمة
translations = {
    "lang_choice": {"ar": "اختر اللغة", "fr": "Choisir la langue"},
    "title": {"ar": "🏗️ مشروع التخرج - حساب العزل الحراري", "fr": "🏗️ Projet de fin d'études - Calcul d'isolation thermique"},
    "wilaya": {"ar": "اختر الولاية:", "fr": "Choisir la wilaya:"},
    "dimensions": {"ar": "أدخل أبعاد المبنى", "fr": "Entrer les dimensions du bâtiment"},
    "length": {"ar": "الطول (متر)", "fr": "Longueur (m)"},
    "width": {"ar": "العرض (متر)", "fr": "Largeur (m)"},
    "height": {"ar": "الارتفاع (متر)", "fr": "Hauteur (m)"},
    "wall_area": {"ar": "المساحة الكلية للجدران", "fr": "Surface totale des murs"},
    "paroi": {"ar": "اختر نوع الجدار:", "fr": "Choisir le type de mur:"},
    "depth": {"ar": "عمق الدفن (متر)", "fr": "Profondeur d'enfouissement (m)"},
    "isolation_type": {"ar": "نوع العزل:", "fr": "Type d'isolation:"},
    "ponts": {"ar": "حساب الجسور الحرارية", "fr": "Calcul des ponts thermiques"},
    "result": {"ar": "نتائج الحساب", "fr": "Résultats du calcul"},
    "needs_insulation": {"ar": "⚠️ يحتاج إلى عزل إضافي", "fr": "⚠️ Nécessite une isolation supplémentaire"},
    "ok": {"ar": "✅ مطابق لمتطلبات العزل", "fr": "✅ Conforme aux exigences d'isolation"}
}

# اختيار اللغة
lang = st.radio(translations["lang_choice"]["ar"] + " / " + translations["lang_choice"]["fr"], ["ar", "fr"])
st.title(translations["title"][lang])

# اختيار الولاية
wilayas = [w["name"] for w in communes_data["wilayas"]]
selected_wilaya = st.selectbox(translations["wilaya"][lang], wilayas)

# إدخال الأبعاد
st.subheader(translations["dimensions"][lang])
length = st.number_input(translations["length"][lang], 10.0)
width = st.number_input(translations["width"][lang], 8.0)
height = st.number_input(translations["height"][lang], 3.0)

wall_area = 2 * height * (length + width)
st.write(f"{translations['wall_area'][lang]}: {wall_area:.2f} m²")

# اختيار نوع الجدار
parois = [p["type"] for p in materiaux_data["parois_types"]]
selected_paroi = st.selectbox(translations["paroi"][lang], parois)
paroi_info = next(p for p in materiaux_data["parois_types"] if p["type"] == selected_paroi)
K = paroi_info["coefficient_K_W_m2C"]

st.subheader(translations["result"][lang])
st.write(f"K = {K} W/m²·°C")
if K > 0.6:
    st.error(translations["needs_insulation"][lang])
else:
    st.success(translations["ok"][lang])

# حساب الجدران المدفونة
st.subheader("🏗️ Parois enterrées / الجدران المدفونة")
z = st.number_input(translations["depth"][lang], -6.0, 1.5, -1.5)
isolation_type = st.selectbox(translations["isolation_type"][lang], ["بدون عزل", "Sans isolation", "عزل أفقي كامل", "Isolation horizontale totale"])

if "Sans" in isolation_type or "بدون" in isolation_type:
    valeurs = parois_enterrees["planchers_bas"]["sans_isolation"]["valeurs"]
    ks_value = None
    for v in valeurs:
        if v["z_min"] <= z <= v["z_max"]:
            ks_value = v["ks"]
            break
    if ks_value:
        st.write(f"ks = {ks_value} W/m·°C")

# حساب الجسور الحرارية
st.subheader(translations["ponts"][lang])
ponts = ponts_thermiques["forfaitaire"]["valeur"]
st.write(f"Majoration forfaitaire / الزيادة الافتراضية = {ponts*100}%")
