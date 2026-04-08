import streamlit as st
import json
import trimesh
import plotly.graph_objects as go

# --------------------- إعداد الصفحة ---------------------
st.set_page_config(
    page_title="مشروع التخرج - حساب العزل الحراري",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------- المسارات ---------------------
PATH_COMMUNES = [
    "communes_zone_A.json",
    "communes_zone_B.json",
    "communes_zone_C.json",
    "communes_zone_A1.json",
    "communes_zone_Inconnue.json"
]
PATH_MATERIAUX = "dtr_materiaux.json"
PATH_PAROIS = "dtr_parois_enterrees.json"
PATH_PONTS = "dtr_ponts_thermiques.json"

# --------------------- تحميل البيانات ---------------------
communes_data = []
for path in PATH_COMMUNES:
    with open(path, "r", encoding="utf-8") as f:
        communes_data.extend(json.load(f))

with open(PATH_MATERIAUX, "r", encoding="utf-8") as f:
    materiaux_data = json.load(f)
with open(PATH_PAROIS, "r", encoding="utf-8") as f:
    parois_enterrees = json.load(f)
with open(PATH_PONTS, "r", encoding="utf-8") as f:
    ponts_thermiques = json.load(f)

# --------------------- الترجمة ---------------------
translations = {
    "lang_choice": {"ar": "اختر اللغة", "fr": "Choisir la langue"},
    "title": {"ar": "مشروع التخرج - حساب العزل الحراري", "fr": "Projet de fin d'études - Calcul d'isolation thermique"},
    "wilaya": {"ar": "اختر الولاية:", "fr": "Choisir la wilaya:"},
    "zone": {"ar": "التصنيف الحراري:", "fr": "Zone thermique:"},
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
    "needs_insulation": {"ar": "يحتاج إلى عزل إضافي", "fr": "Nécessite une isolation supplémentaire"},
    "ok": {"ar": "مطابق لمتطلبات العزل", "fr": "Conforme aux exigences d'isolation"},
    "3d_model": {"ar": "نموذج ثلاثي الأبعاد", "fr": "Modèle 3D"}
}

# --------------------- اختيار الثيم ---------------------
theme_choice = st.sidebar.radio("Theme / الثيم", ["Light", "Dark"])
if theme_choice == "Dark":
    primary_color = "#0F52BA"
    background_color = "#111111"
    text_color = "#FFFFFF"
else:
    primary_color = "#0F52BA"
    background_color = "#FFFFFF"
    text_color = "#000000"

# --------------------- تطبيق الخطوط والستايل ---------------------
st.markdown(
    f"""
    <style>
        body, .reportview-container {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            background-color: {background_color};
            color: {text_color};
        }}
        .sidebar .sidebar-content {{
            background-color: {primary_color};
            color: #FFFFFF;
            font-family: 'Arial', 'Helvetica', sans-serif;
        }}
        .stButton>button {{
            background-color: {primary_color};
            color: white;
            border-radius: 8px;
            height: 38px;
        }}
        .stSelectbox>div>div>div>div {{
            border-radius: 8px;
            border: 1px solid {primary_color};
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Arial', 'Helvetica', sans-serif;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------- اختيار اللغة ---------------------
lang = st.sidebar.radio(
    translations["lang_choice"]["ar"] + " / " + translations["lang_choice"]["fr"],
    ["ar", "fr"],
    key="lang_choice"
)
st.title(translations["title"][lang])

# --------------------- اختيار الولاية ---------------------
wilayas = [f"{w['name']} ({w['thermal_zone_winter']})" for w in communes_data]
selected_wilaya = st.sidebar.selectbox(
    translations["wilaya"][lang],
    wilayas,
    key="wilaya_choice"
)
wilaya_info = next(w for w in communes_data if f"{w['name']} ({w['thermal_zone_winter']})" == selected_wilaya)
zone = wilaya_info["thermal_zone_winter"]
st.write(f"{translations['zone'][lang]} {zone}")

# --------------------- إدخال الأبعاد ---------------------
st.sidebar.subheader(translations["dimensions"][lang])
length = st.sidebar.number_input(translations["length"][lang], 10.0, key="length_input")
width = st.sidebar.number_input(translations["width"][lang], 8.0, key="width_input")
height = st.sidebar.number_input(translations["height"][lang], 3.0, key="height_input")

wall_area = 2 * height * (length + width)
st.write(f"{translations['wall_area'][lang]}: {wall_area:.2f} m²")

# --------------------- اختيار نوع الجدار ---------------------
parois = [p["type"] for p in materiaux_data["parois_types"]]
selected_paroi = st.sidebar.selectbox(
    translations["paroi"][lang],
    parois,
    key="paroi_choice"
)
paroi_info = next(p for p in materiaux_data["parois_types"] if p["type"] == selected_paroi)
K = paroi_info["coefficient_K_W_m2C"]

# --------------------- عرض النتائج ---------------------
st.subheader(translations["result"][lang])
col1, col2 = st.columns(2)
with col1:
    st.metric("K (W/m²·°C)", f"{K:.2f}")
    if K > 0.6:
        st.error(translations["needs_insulation"][lang])
    else:
        st.success(translations["ok"][lang])
with col2:
    st.write(f"{translations['wall_area'][lang]}: {wall_area:.2f} m²")

# --------------------- الجدران المدفونة ---------------------
st.sidebar.subheader(translations["depth"][lang])
z = st.sidebar.number_input(translations["depth"][lang], -6.0, 1.5, -1.5, key="depth_input")
isolation_type = st.sidebar.selectbox(
    translations["isolation_type"][lang],
    ["بدون عزل", "Sans isolation", "عزل أفقي كامل", "Isolation horizontale totale"],
    key="isolation_choice"
)
if "Sans" in isolation_type or "بدون" in isolation_type:
    valeurs = parois_enterrees["planchers_bas"]["sans_isolation"]["valeurs"]
    ks_value = None
    for v in valeurs:
        if v["z_min"] <= z <= v["z_max"]:
            ks_value = v["ks"]
            break
    if ks_value:
        st.write(f"ks = {ks_value} W/m·°C")

# --------------------- الجسور الحرارية ---------------------
st.subheader(translations["ponts"][lang])
ponts = ponts_thermiques["forfaitaire"]["valeur"]
st.write(f"الزيادة الافتراضية = {ponts*100}%")

# --------------------- عرض النموذج الثلاثي الأبعاد ---------------------
st.subheader(translations["3d_model"][lang])
uploaded_file = st.file_uploader("Upload 3D Model", type=["obj", "stl", "ply", "3ds"], key="3d_upload")
if uploaded_file is not None:
    try:
        mesh = trimesh.load(uploaded_file, file_type=None)
        vertices = mesh.vertices
        faces = mesh.faces
        fig = go.Figure(data=[
            go.Mesh3d(
                x=vertices[:,0],
                y=vertices[:,1],
                z=vertices[:,2],
                i=faces[:,0],
                j=faces[:,1],
                k=faces[:,2],
                color=primary_color,
                opacity=0.50,
            )
        ])
        fig.update_layout(
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode="data",
                camera=dict(eye=dict(x=1.5, y=1.5, z=1))
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor=background_color
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"تعذر قراءة الملف: {e}")
