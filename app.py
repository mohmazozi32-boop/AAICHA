import streamlit as st
import json
from scripts import categorize2, Evaluation_Formules_DTR, zonage1

# إعداد الصفحة
st.set_page_config(page_title="Évaluation Thermique Algérie", layout="wide")

st.title("منصة تقييم العزل الحراري - الجزائر 🇩🇿")

# تحميل بيانات الولايات
with open("data/data_communes_algeria.json", "r", encoding="utf-8") as f:
    data = json.load(f)

wilayas = [w["name"] for w in data["wilayas"]]

# اختيار الولاية
wilaya = st.selectbox("اختر الولاية", options=wilayas)

# استدعاء محرك المناخ
climate_engine = zonage1.AlgerianClimateEnricher()
wilaya_data = climate_engine.find_wilaya_by_name(wilaya, data["wilayas"])

zone_hiver, tbe = climate_engine.determine_winter_zone(wilaya_data, data["wilayas"])
zone_ete, conditions = climate_engine.determine_summer_zone(wilaya_data, data["wilayas"])

st.subheader("📊 النتائج المناخية")
st.write(f"Zone Hiver: {zone_hiver}, Température de base: {tbe} °C")
st.write(f"Zone Été: {zone_ete}")
st.json(conditions)

# مثال حساب حراري باستخدام Evaluation_Formules_DTR
from scripts.Evaluation_Formules_DTR import MoteurFormulesDTR, Paroi, TypeIsolation
moteur = MoteurFormulesDTR()
paroi1 = Paroi("Mur béton", TypeIsolation.REPARTIE, 0.5, 0.2, 2.0)
paroi2 = Paroi("Mur brique", TypeIsolation.REPARTIE, 0.6, 0.25, 1.8)
kl = moteur.calculer_kl_liaison_deux_parois("isolation_repartie_identiques", paroi1, paroi2)

st.subheader("⚙️ حساب معامل الجسر الحراري")
st.write(f"kl = {kl} W/m.°C")

# واجهة ثنائية اللغة (عربية/فرنسية)
lang = st.radio("Choisir la langue / اختر اللغة", ["Français", "العربية"])
if lang == "العربية":
    st.success("تم اختيار اللغة العربية")
else:
    st.success("Langue française sélectionnée")

# وضع نهار/ليل
theme = st.radio("Mode d'affichage", ["Jour", "Nuit"])
if theme == "Nuit":
    st.markdown("<style>body{background-color:#1e1e1e;color:white;}</style>", unsafe_allow_html=True)
