import streamlit as st
import pandas as pd
import os

# Configuration de la page
st.set_page_config(page_title="🎄 Liste de Noël 2025", layout="wide")

# CSS personnalisé pour augmenter la taille du texte
st.markdown("""
<style>
    /* Augmenter la taille du texte dans le tableau */
    .stDataFrame, .stDataFrame td, .stDataFrame th {
        font-size: 22px !important;
    }
    
    /* Augmenter la taille du texte général */
    .stMarkdown, p, div, span, label {
        font-size: 20px !important;
    }
    
    /* Augmenter la taille du titre */
    h1 {
        font-size: 48px !important;
    }
    
    /* Augmenter la taille des selectbox */
    .stSelectbox label {
        font-size: 24px !important;
    }
    
    /* Augmenter la taille des métriques */
    .stMetric label, .stMetric .metric-value {
        font-size: 22px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎄 Liste de Noël 2025")
st.subheader("Cher Papa Noël, on a tous été super sages cette année !! Promis ;o)")

# Chemin vers le fichier CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "noel_2025.csv")

# Fonction pour charger les données
def load_data():
    try:
        df = pd.read_csv(CSV_PATH, sep=';', encoding='utf-8-sig')
        df['choisi'] = df['choisi'].astype(bool)
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du CSV : {e}")
        st.stop()

# Fonction pour sauvegarder les données
def save_data(df):
    df.to_csv(CSV_PATH, sep=';', index=False, encoding='utf-8-sig')

# Charger les données UNIQUEMENT si elles ne sont pas déjà en session
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# Filtre par personne
personnes = ['Tous'] + sorted(st.session_state.data['pour'].dropna().unique().tolist())
personne_selectionnee = st.selectbox("🎁 Filtrer par personne :", personnes)

# Filtrer les données
if personne_selectionnee == 'Tous':
    data_filtree = st.session_state.data.copy()
else:
    data_filtree = st.session_state.data[st.session_state.data['pour'] == personne_selectionnee].copy()

# Afficher le tableau éditable
edited_df = st.data_editor(
    data_filtree,
    column_config={
        "cadeau": st.column_config.TextColumn("🎁 Cadeau", width="large"),
        "pour": st.column_config.TextColumn("👤 Pour", width="small"),
        "lien": st.column_config.LinkColumn("🔗 Lien", width="large"),
        "img": st.column_config.ImageColumn("📷 Image", width="small"),
        "choisi": st.column_config.CheckboxColumn("✅ Choisi", width="small"),
        "plusieurs": st.column_config.CheckboxColumn("👥 On peut se mettre à plusieurs !", width="medium"),
    },
    column_order=["choisi", "plusieurs", "cadeau", "pour", "lien", "img"],
    hide_index=True,
    use_container_width=True,
    disabled=["cadeau", "pour", "lien", "img", "plusieurs"],  # Seule les cases "choisi" et "plusieurs" sont éditables
    key="data_editor"  # Clé importante pour la persistence
)

# Détecter les changements et mettre à jour
if not edited_df.equals(data_filtree):
    # Mettre à jour les données dans la session pour les lignes modifiées
    for idx in edited_df.index:
        st.session_state.data.loc[idx, 'choisi'] = edited_df.loc[idx, 'choisi']
        st.session_state.data.loc[idx, 'plusieurs'] = edited_df.loc[idx, 'plusieurs']
    
    # Sauvegarder dans le CSV
    save_data(st.session_state.data)

st.rerun()  # Forcer le rechargement pour afficher les changements

# Afficher un résumé
col1, col2 = st.columns(2)

with col1:
    nb_choisis_filtre = edited_df['choisi'].sum()
    st.metric("Items sélectionnés (filtrés)", f"{int(nb_choisis_filtre)} / {len(edited_df)}")

with col2:
    nb_choisis_total = st.session_state.data['choisi'].sum()
    st.metric("Total sélectionnés", f"{int(nb_choisis_total)} / {len(st.session_state.data)}")

# Bouton pour recharger depuis le fichier (utile si quelqu'un d'autre modifie)
if st.button("🔄 Recharger depuis le fichier"):
    st.session_state.data = load_data()
    st.rerun()
