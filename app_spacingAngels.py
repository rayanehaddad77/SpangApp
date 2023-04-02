import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import sqlite3
from streamlit_option_menu import option_menu


# Titre de la page
st.set_page_config(page_title="SpangApp", page_icon="logo_spacing_angels.jpg", layout="wide")

# En-tête de la page
st.markdown(
    """
    <div style='background-color:#F63366;padding:10px'>
        <h2 style='color:white;text-align:center;'>	🚗 SpangApp - Suivi des véhicules 🚗</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# Connexion à la base de données
conn = sqlite3.connect('app_spacingAngelsBDD_generated.db')

# Exécution de requêtes SQL pour extraire des données de la table
iteration_df = pd.read_sql_query("SELECT * FROM iteration", conn)
plate_box_df = pd.read_sql_query("SELECT * FROM plate_box", conn)
run_parameters_df = pd.read_sql_query("SELECT * FROM run_parameters", conn)
travel_df = pd.read_sql_query("SELECT * FROM travel", conn)

# Menu de navigation latéral

with st.sidebar:
    selected = option_menu("Menu", ["🏠 Accueil", "📋Tableau de bord", "🌍 Carte", "📈 Graphique", "📊 Statistiques"], 
        default_index=0)
    

if selected == "🏠 Accueil":

    image = 'image_home.jpg'
    st.image(image, use_column_width=True, width=500)

    st.markdown("""
        <style>
        .big-font {
            font-size:25px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("""<p class="big-font"> La sécurité routière est une préoccupation majeure pour les gouvernements et les entreprises du monde entier. Chaque année, les accidents de la route causent des milliers de morts et de blessés, ce qui représente un coût élevé en termes humains, économiques et sociaux. Dans ce contexte, le développement de nouvelles technologies pour améliorer la sécurité routière est crucial pour notre société. </p>""", unsafe_allow_html=True)
    st.markdown("""<p class="big-font"> Parmi les accidents les plus fréquents, les collisions arrières représentent une menace particulièrement importante. C'est pourquoi Baucher Etudes & Conseils (BEC), une startup spécialisée dans la conception et l'étude de produits innovants pour la sécurité routière, a développé le radar pédagogique autonome Spacing Angels. Cette solution permet de prévenir les collisions arrières en alertant les conducteurs des véhicules de la proximité des autres véhicules. Avec Spacing Angels, BEC offre une solution efficace et facile à utiliser pour améliorer la sécurité routière. </p>""", unsafe_allow_html=True)

elif selected == "📋Tableau de bord":
    st.markdown("<div style='text-align:center'><h2>Tableau de bord</h2></div>", unsafe_allow_html=True)
    st.write(
        """
        Voici les données des différentes tables de la base de données.
        """
    )
    
    # Menu déroulant pour sélectionner les données à afficher
    options = ['Iteration', 'Plate Box', 'Run Parameters', 'Travel']
    selection = st.selectbox('Sélectionnez les données à afficher', options)

    # Chargement des données sélectionnées
    if selection == 'Iteration':
        data = iteration_df
    elif selection == 'Plate Box':
        data = plate_box_df
    elif selection == 'Run Parameters':
        data = run_parameters_df
    else:
        data = travel_df

    # Affichage des données
    st.write(data)

elif selected == "🌍 Carte":
    st.markdown("<div style='text-align:center'><h2>Carte</h2></div>", unsafe_allow_html=True)
    st.write(
        """
        Voici la carte des positions des véhicules et le tracé de leurs itinéraires.
        """
    )

    # Créer une liste des identifiants de voyage uniques
    travel_ids = iteration_df['travel_id'].unique().tolist()

    # Menu déroulant pour sélectionner le voyage à afficher
    selected_travel_id = st.selectbox('Sélectionnez le voyage à afficher', travel_ids)

    # Filtrer les données pour le voyage sélectionné et trier par ordre chronologique
    travel_data = iteration_df.loc[iteration_df['travel_id'] == selected_travel_id].sort_values('timestamp')

    # Extraire les coordonnées de la première et de la dernière itération de l'itinéraire
    start_coords = [travel_data.iloc[0]['latitude'], travel_data.iloc[0]['longitude']]
    end_coords = [travel_data.iloc[-1]['latitude'], travel_data.iloc[-1]['longitude']]

    # Créer une liste de coordonnées pour le tracé de ligne sur la carte
    line_coords = [start_coords] + travel_data.iloc[1:-1][['latitude', 'longitude']].values.tolist() + [end_coords]

    # Afficher la carte des positions des véhicules pour le voyage sélectionné avec le tracé de ligne
    fig = px.scatter_mapbox(travel_data, lat='latitude', lon='longitude', zoom=10)
    fig.update_layout(mapbox_style="open-street-map")
    fig.add_trace(px.line_mapbox(lat=[coord[0] for coord in line_coords], lon=[coord[1] for coord in line_coords]).data[0])
    st.plotly_chart(fig)

elif selected == "📈 Graphique":
    # Récupérer les données de temps et de distance à partir de la dataframe iteration
    timestamps = iteration_df['timestamp'].values.tolist()
    distances = iteration_df['distance'].cumsum().values.tolist()

    # Créer une dataframe pour le graphique
    df_graphique = pd.DataFrame({'timestamp': timestamps, 'distance': distances})

    # Tracer le graphique
    graphique = alt.Chart(df_graphique).mark_line().encode(
        x='timestamp:T',
        y='distance:Q'
    ).properties(
        width=700,
        height=400,
        title='Distance parcourue en fonction du temps'
    )

    # Afficher le graphique dans l'application Streamlit
    st.markdown("<h2 style='text-align: center'>Graphique de la distance parcourue</h2>", unsafe_allow_html=True)
    st.altair_chart(graphique, use_container_width=True)

    

elif selected == "📊 Statistiques":
    # Afficher les histogrammes sur la même ligne
    col1, col2 = st.columns(2)

    # Afficher un histogramme de la vitesse moyenne par voyage dans la première colonne
    with col1:
        st.markdown("<h2 style='text-align: center'>Histogramme de la vitesse moyenne par voyage</h2>", unsafe_allow_html=True)
        avg_speed_by_travel = iteration_df.groupby('travel_id').mean(numeric_only=True)['speed']
        fig = px.histogram(avg_speed_by_travel, x='speed', nbins=20)
        st.plotly_chart(fig)

    # Afficher un histogramme de la vitesse des véhicules ayant une plaque détectée dans la deuxième colonne
    with col2:
        st.markdown("<h2 style='text-align: center'>Répartition des plaques detectées en fonction de la vitesse du véhicule</h2>", unsafe_allow_html=True)
        # Filtrer les itérations où une plaque d'immatriculation a été détectée
        detections = iteration_df[iteration_df["status"] == "PlateDetected"]
        # Créer un histogramme de la vitesse des véhicules ayant une plaque détectée
        histogram = alt.Chart(detections).mark_bar().encode( x=alt.X("speed", bin=True), y="count()" ).properties( width=700, height=400 )
        # Afficher le graphique
        st.altair_chart(histogram)

