import streamlit as st
import json
import os

# =========================
# CONFIGURATION
# =========================
st.set_page_config(page_title="DTR Thermal Analysis System", layout="wide")

DATA_FILES = [
    "data_communes_algeria.json",
    "communes_zone_A.json",
    "communes_zone_B.json",
    "communes_zone_C.json",
    "communes_zone_Inconnue.json",
]

# =========================
# DATA LOADING LAYER
# =========================
def load_communes():
    dataset = []

    for file in DATA_FILES:
        if not os.path.exists(file):
            continue

        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "name" in item:
                            dataset.append(item)

        except Exception:
            continue

    return dataset


communes = load_communes()


# =========================
# THERMAL ENGINE (SIMPLIFIED DTR CORE)
# =========================
class ThermalEngine:

    @staticmethod
    def evaluate(zone, wall_r, roof_r, insulation_type):
        score = 0.0

        zone_weights = {
            "A": 1.2,
            "B": 1.0,
            "C": 0.8,
            "Inconnue": 1.0
        }

        score += zone_weights.get(zone, 1.0)

        # Walls
        if wall_r >= 2.5:
            score += 1.5
        elif wall_r >= 1.5:
            score += 1.0
        else:
            score += 0.3

        # Roof
        if roof_r >= 3.0:
            score += 1.5
        elif roof_r >= 2.0:
            score += 1.0
        else:
            score += 0.4

        # Insulation system
        if insulation_type == "exterieure":
            score += 1.2
        elif insulation_type == "interieure":
            score += 0.8
        else:
            score += 1.0

        return score

    @staticmethod
    def decision(score):
        if score >= 4.0:
            return "Conforme"
        elif score >= 3.0:
            return "Acceptable"
        return "Non conforme"


engine = ThermalEngine()


# =========================
# VALIDATION
# =========================
if not communes:
    st.error("Aucune donnée chargée. Vérifier les fichiers JSON.")
    st.stop()


# =========================
# UI LAYER
# =========================
st.title("DTR Thermal Building Verification System")

st.write(
    "Système d’évaluation thermique basé sur les données communales et paramètres du bâtiment."
)


# =========================
# CITY SELECTION
# =========================
cities = sorted([
    c.get("name")
    for c in communes
    if isinstance(c, dict) and c.get("name")
])

selected_city = st.selectbox("Commune", cities)

city = next((c for c in communes if c.get("name") == selected_city), None)


# =========================
# INPUT PARAMETERS
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    insulation_type = st.selectbox(
        "Système d’isolation",
        ["repartie", "interieure", "exterieure"]
    )

with col2:
    wall_r = st.number_input("Résistance thermique murs (R)", 0.1, 10.0, 1.5)

with col3:
    roof_r = st.number_input("Résistance thermique toiture (R)", 0.1, 10.0, 2.0)


# =========================
# CITY INFORMATION PANEL
# =========================
if city:
    st.subheader("Données climatiques de la commune")

    st.write({
        "Nom": city.get("name"),
        "Nom arabe": city.get("name_ar"),
        "Zone thermique hiver": city.get("thermal_zone_winter"),
        "Altitude": city.get("elevation"),
        "Latitude": city.get("latitude"),
        "Longitude": city.get("longitude")
    })


# =========================
# ANALYSIS
# =========================
if st.button("Lancer l’évaluation thermique"):

    if not city:
        st.error("Commune non valide")
        st.stop()

    zone = city.get("thermal_zone_winter", "Inconnue")

    score = engine.evaluate(zone, wall_r, roof_r, insulation_type)
    result = engine.decision(score)

    st.subheader("Résultat de l’analyse")

    st.write("Statut :", result)
    st.write("Score :", round(score, 2))


    # Engineering interpretation
    st.subheader("Interprétation technique")

    if result == "Non conforme":
        st.write("Le bâtiment présente des pertes thermiques importantes.")
        st.write("Recommandation : augmentation de l’isolation ou correction des ponts thermiques.")

    elif result == "Acceptable":
        st.write("Performance moyenne. Optimisation recommandée.")
        st.write("Recommandation : améliorer toiture et traitement des jonctions.")

    else:
        st.write("Performance thermique conforme aux exigences générales.")
        st.write("Système d’isolation globalement cohérent.")
