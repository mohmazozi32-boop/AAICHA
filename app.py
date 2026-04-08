import streamlit as st
import json
import plotly.graph_objects as go

# ---------- إعداد الصفحة ----------
st.set_page_config(page_title="Thermal Building App", layout="wide")

# ---------- تحميل البيانات ----------
PATH_COMMUNES = "data_communes_algeria.json"
PATH_MATERIAUX = "dtr_materiaux.json"
PATH_PAROIS = "dtr_parois_enterrees.json"
PATH_PONTS = "dtr_ponts_thermiques.json"

with open(PATH_COMMUNES, "r", encoding="utf-8") as f:
    communes_data = json.load(f)

with open(PATH_MATERIAUX, "r", encoding="utf-8") as f:
    materiaux_data = json.load(f)

with open(PATH_PAROIS, "r", encoding="utf-8") as f:
    parois_enterrees = json.load(f)

with open(PATH_PONTS, "r", encoding="utf-8") as f:
    ponts_thermiques = json.load(f)

# ---------- الترجمة ----------
translations = {
    "title": {"ar": "🏗️ حساب العزل الحراري + نموذج 3D", "fr": "🏗️ Calcul thermique + modèle 3D"},
    "wilaya": {"ar": "اختر الولاية", "fr": "Choisir la wilaya"},
    "dimensions": {"ar": "أبعاد المبنى", "fr": "Dimensions du bâtiment"},
    "length": {"ar": "الطول", "fr": "Longueur"},
    "width": {"ar": "العرض", "fr": "Largeur"},
    "height": {"ar": "الارتفاع", "fr": "Hauteur"},
    "paroi": {"ar": "نوع الجدار", "fr": "Type de mur"},
    "result": {"ar": "النتائج", "fr": "Résultats"},
    "depth": {"ar": "عمق الدفن", "fr": "Profondeur"},
    "isolation": {"ar": "نوع العزل", "fr": "Type isolation"}
}

# ---------- اختيار اللغة ----------
lang = st.sidebar.radio("Language / اللغة", ["ar", "fr"])

# ---------- العنوان ----------
st.title(translations["title"][lang])

# ---------- Sidebar ----------
st.sidebar.header("⚙️ Paramètres")

wilayas = [w["name"] for w in communes_data["wilayas"]]
selected_wilaya = st.sidebar.selectbox(translations["wilaya"][lang], wilayas)

length = st.sidebar.slider(translations["length"][lang], 1, 50, 10)
width = st.sidebar.slider(translations["width"][lang], 1, 50, 8)
height = st.sidebar.slider(translations["height"][lang], 1, 50, 3)

# ---------- حساب المساحة ----------
wall_area = 2 * height * (length + width)

# ---------- اختيار الجدار ----------
parois = [p["type"] for p in materiaux_data["parois_types"]]
selected_paroi = st.sidebar.selectbox(translations["paroi"][lang], parois)
paroi_info = next(p for p in materiaux_data["parois_types"] if p["type"] == selected_paroi)
K = paroi_info["coefficient_K_W_m2C"]

# ---------- Layout ----------
col1, col2 = st.columns([1, 2])

# ---------- معلومات ----------
with col1:
    st.subheader("📊 Infos")
    st.write(f"Surface murs = {wall_area:.2f} m²")
    st.write(f"K = {K}")

    if K > 0.6:
        st.error("⚠️ Mauvaise isolation")
        color = "red"
    else:
        st.success("✅ Bonne isolation")
        color = "green"

# ---------- 3D Model ----------
with col2:
    st.subheader("🏗️ Modèle 3D")

    x = [0, length, length, 0, 0, length, length, 0]
    y = [0, 0, width, width, 0, 0, width, width]
    z_vals = [0, 0, 0, 0, height, height, height, height]

    fig = go.Figure(data=[
        go.Mesh3d(
            x=x,
            y=y,
            z=z_vals,
            opacity=0.7,
            color=color
        )
    ])

    fig.update_layout(
        scene=dict(
            xaxis_title='L',
            yaxis_title='W',
            zaxis_title='H'
        ),
        margin=dict(l=0, r=0, b=0, t=0)
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------- Parois enterrées ----------
st.subheader("🏗️ Parois enterrées")

z = st.slider(translations["depth"][lang], -6.0, 1.5, -1.5)

isolation_type = st.selectbox(
    translations["isolation"][lang],
    ["Sans isolation", "Isolation horizontale totale"]
)

if "Sans" in isolation_type:
    valeurs = parois_enterrees["planchers_bas"]["sans_isolation"]["valeurs"]
    ks_value = None

    for v in valeurs:
        if v["z_min"] <= z <= v["z_max"]:
            ks_value = v["ks"]
            break

    if ks_value:
        st.write(f"ks = {ks_value} W/m·°C")

# ---------- Ponts thermiques ----------
st.subheader("🌡️ Ponts thermiques")

ponts = ponts_thermiques["forfaitaire"]["valeur"]
st.write(f"Majoration = {ponts*100}%")
