
# Dash
from dash import Dash, dcc, html, Input, Output, State, ctx, ALL
import dash_bootstrap_components as dbc
import dash.dependencies as dd

import glob
import os
import gdown
import geopandas as gpd
import pandas as pd


# Visualisations
import plotly.express as px
import plotly.graph_objects as pgo
import dash
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = "notebook_connected"

# Enlever les warnings
import warnings
warnings.filterwarnings("ignore")

# Importation des fichiers de données lourds hébergé sur google drive
import load_data

# Application
app = dash.Dash(__name__, suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.BOOTSTRAP])

programme_pvd = pd.read_csv("data_dashboard/programme_pvd.csv",sep=";",low_memory=False)
contours_des_regions = gpd.read_file("data_dashboard/contours-des-regions.geojson")
contours_des_departements = gpd.read_file("data_dashboard/contour-des-departements.geojson")
contours_des_communes = gpd.read_file("data_dashboard/contours_communes.json")
donnees_communes = pd.read_csv("data_dashboard/donnees_communes.csv",sep=";",low_memory=False)
naissances = pd.read_csv("data_dashboard/naissances.csv",sep=",",low_memory=False)
deces = pd.read_csv("data_dashboard/deces.csv",sep=",",low_memory=False)
data_age_population_generale = pd.read_csv("data_dashboard/data_age_population_generale.csv",sep=",",low_memory=False)
data_age_selon_sexe = pd.read_csv("data_dashboard/data_age_selon_sexe.csv",sep=",",low_memory=False)
data_cs_selon_sexe = pd.read_csv("data_dashboard/data_cs_selon_sexe.csv",sep=',',low_memory=False)


donnees_communes = donnees_communes.rename(
    columns = {"COM" : "insee_com", 
               "CODCAN" : "Communauté de commune",
               "DEP" : "Département"}
)
naissances = naissances.merge(
    donnees_communes[["insee_com", "Communauté de commune", "Département", "Région"]], 
    on = 'insee_com', 
    how = 'left'
)
deces = deces.merge(
    donnees_communes[["insee_com", "Communauté de commune", "Département", "Région"]], 
    on = 'insee_com', 
    how = 'left'
)
data_age_population_generale = data_age_population_generale.merge(
    donnees_communes[["insee_com", "Communauté de commune", "Département", "Région"]], 
    on = 'insee_com', 
    how = 'left'
)
data_age_selon_sexe = data_age_selon_sexe.merge(
    donnees_communes[["insee_com", "Communauté de commune", "Département", "Région"]], 
    on = 'insee_com', 
    how = 'left'
)
data_cs_selon_sexe = data_cs_selon_sexe.merge(
    donnees_communes[["insee_com", "Communauté de commune", "Département", "Région"]], 
    on = 'insee_com', 
    how = 'left'
)
naissances = naissances.merge(
    data_age_population_generale[data_age_population_generale["Tranche_age"] == "Total"][["insee_com", "Année", "Effectif"]],
    on = ("insee_com", "Année"),
    how = 'left'
)
deces = deces.merge(
    data_age_population_generale[data_age_population_generale["Tranche_age"] == "Total"][["insee_com", "Année", "Effectif"]],
    on = ("insee_com", "Année"),
    how = 'left'
)


# ### Couleurs

# Défintion des couleurs

# Page acceuil
col_emplacement_communes = "#8b508d"
grad_violet_rose = "RdPu"

# Bouton information et switch
col_bouton = '#aea6bd'
col_fermeture_bouton_info = '#00202e'

# Général application 
col_background = '#f8f9fa'
col_navbar_text = '#fef8f7'
col_navbar = '#463c57'

# Treemap classes-sociales
color_dict = {
    "Population" : "#d3d3d3",
    "Agriculteurs" : "#154660", 
    "Artisants et commerçants" : "#5c558c", 
    "Autres" : "#89558e", 
    "Cadres" : "#b7568e",
    "Employés" : "#d6607a", 
    "Ouvriers" : "#f36865", 
    "Professions intermédiaires" : "#f38640", 
    "Retraités" : "#f2a32d", 
    "F" : "#b05fc5",
    "H":"#fcb869"
}

# Graphiques
col_plot_background = "#d3d3d3"

col_deces = "#ff8a88"
col_deces_darker = "#803231"

col_naissances = "#00c0c0"
col_naissances_darker= "#005050"

col_population = "#c075c2"
col_population_darker = "#533055"

col_femme = "#b05fc5"
col_homme = "#fcb869"

col_commune = "#ba1a1a"
col_territoire = "#d9d9d9"
col_contours = "#c9c9c9"


# # 1 Page d'acceuil

# KPI Nombre de communes dans le programme
nombres_petites_villes = programme_pvd["insee_com"].count()

# Données pour les cartes
lat_long = programme_pvd['Geo Point'].apply(lambda point: point.split(','))
programme_pvd['lat'] = [float(x[0]) for x in lat_long]
programme_pvd['long'] = [float(x[1]) for x in lat_long]

# Carte emplacement des pvd
carte_emplacement_pvd = px.scatter_mapbox(
    programme_pvd, lat="lat", lon="long",
    mapbox_style="carto-positron", # fond de la carte
    custom_data=["lib_com","insee_com","Nom Officiel Département","Nom Officiel Région"], # pour customiser les variables qui appraissent dans l'étiquette (quand on survole)
    zoom=3.6, center={'lat':46.7,'lon':4},
    title="<b>Emplacement des communes membres du programme</b>"
)
carte_emplacement_pvd.update_traces(marker=dict(color=col_emplacement_communes,size=4),hovertemplate="<br>".join(["<b>Nom :</b> %{customdata[0]}","<b>Code INSEE :</b> %{customdata[1]}","<b>Département :</b> %{customdata[2]}","<b>Région :</b> %{customdata[3]}"])) # Pour customiser les variables qui apparaissent dans l'étiquette


# Carte pvd par départements
nb_communes_dep = programme_pvd['Code Officiel Département'].value_counts().reset_index().rename(
    {'Code Officiel Département': 'code', 'count': 'nb_communes'},
    axis=1
)
merged = gpd.GeoDataFrame(
    pd.merge(
        nb_communes_dep,
        contours_des_departements[['code','nom', 'geometry']]
    ),
    geometry='geometry',
)
carte_pvd_departements = px.choropleth_mapbox(merged,
                           geojson= merged["geometry"],
                           locations= merged.index,
                           mapbox_style= "carto-positron",
                           color= "nb_communes", # Variable choisie pour la coloration
                           color_continuous_scale=grad_violet_rose, # Choix du dégradé utilisé
                           range_color=(0,40), #Dégradé pour les valeurs de 1 à 50
                           zoom=3.6, center={'lat':46.7,'lon':4}, # Position par défaut
                           opacity=0.7, # Niveau de transparence des couleurs des polygones
                           title="<b>Nombre de Petites Villes de Demain par départements</b>",
                           labels={'nb_communes':'Nombre de communes'},
                           custom_data=["code","nom","nb_communes"]
                           )
carte_pvd_departements.update_traces(hovertemplate="<br>".join(["<b>N° département :</b> %{customdata[0]}","<b>Nom :</b> %{customdata[1]}","<b>Petites villes de demain :</b> %{customdata[2]}"])) # Pour customiser les variables qui apparaissent dans l'étiquette

# Carte pvd par régions
nb_communes_reg = programme_pvd['Code Officiel Région'].value_counts().reset_index().rename(
    {'Code Officiel Région': 'code', 'count': 'nb_communes'},
    axis=1
)
contours_des_regions = contours_des_regions.astype({"code": int})
merged_reg = gpd.GeoDataFrame(
    pd.merge(
        nb_communes_reg,
        contours_des_regions[['code','nom', 'geometry']],
        on = 'code'
    ),
    geometry='geometry',
)
carte_pvd_regions = px.choropleth_mapbox(merged_reg,
                           geojson= merged_reg["geometry"],
                           locations= merged_reg.index,
                           mapbox_style= "carto-positron",
                           color= "nb_communes", # Variable choisie pour la coloration
                           color_continuous_scale=grad_violet_rose, # Choix du dégradé utilisé
                           range_color=(0,230), #Dégradé pour les valeurs de 1 à 250
                           zoom=3.6, center={'lat':46.7,'lon':4}, # Position par défaut
                           opacity=0.7, # Niveau de transparence des couleurs des polygones
                           custom_data=["nom","nb_communes"], #Info-bulle
                           title="<b>Nombre de Petites Villes de Demain par régions</b>",
                           labels={'nb_communes':'Nombre de communes'}
                           )
carte_pvd_regions.update_traces(hovertemplate="<br>".join(["<b>Région :</b> %{customdata[0]}","<b>Petites villes de demain :</b> %{customdata[1]}"])) # Pour customiser les variables qui apparaissent dans l'étiquette



home_layout = html.Div([
    # Première partie Texte
    html.Div([
        # Titre
        html.H1(html.B("Dashboard : La démographie des Petites Villes de Demain"), style={'textAlign': 'center'}),
        # Texte
        html.P(
            ["Les petites villes de demain sont des communes de moins de 20 000 habitants jouant un rôle de centralité sur leur bassin de vie au travers de fonctions administratives, économiques, culturelles, commerciales, de santé, etc. Depuis 2020, l’Agence Nationale de la Cohésion des Territoires (ANCT) et la Banque des Territoires ont mis en place le programme ", 
             html.B("Petites Villes de Demain"), 
             " (PVD) dans le but de les accompagner. Le problème : ces petites villes de demain n’ont pas vraiment de profil type et nécessitent donc un accompagnement personnalisé adapté à ", 
             html.B("leurs besoins et leurs enjeux"), ".", html.Br(),
             "Ce dashboard a donc pour objectif de ", 
             html.B("synthétiser les dynamiques démographiques"), 
             " de chacune des communes membres du programme et ainsi saisir ", 
             html.B("leurs spécificités"), ".", html.Br(), 
             "Pour cela, nous vous proposons une première page regroupant les ", 
             html.B("données démographiques d’une PVD sélectionnée"), 
             " puis une seconde page permettant de ", 
             html.B("comparer"), 
             " la commune sélectionnée avec ", 
             html.B("son canton, son département ou sa région"), 
             " sur des aspects ", 
             html.B("d’âge de population, de profession"), 
             " ou encore ", 
             html.B("d’évolution de population"), "."],
            style={'textAlign': 'justify', 'fontSize': '16px', 'maxWidth': '1250px', 'margin': 'auto'}
        ),
        # Texte en italique
        html.Div([
            html.I(
                "Mieux comprendre ma Petite Ville de Demain pour mieux la construire.",
                style={'fontSize': '16px', 'maxWidth': '800px', 'margin': 'auto'}
            )
            ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'textAlign': 'center', 'marginTop': '20px'}
        )
    ], 
    style={'padding': '20px','font-family': 'Arial'}
    ),
    
    
    # KPI animé du nombre de petites villes
    html.Div([
        # Affichage du KPI
        html.H2(id="kpi-display", style={"fontSize": "60px", "textAlign": "center", "margin-bottom": "5px"}),
        # Texte explicatif
        html.B("Communes membres du programme", style={"textAlign": "center", "fontSize": "20px", "margin-top": "0px"}),
        # Composant pour déclencher l'animation
        dcc.Interval(
            id="interval-component",
            interval=50,  # Temps en ms entre chaque mise à jour
            n_intervals=30,  # Démarre à 0
            max_intervals=100  # Nombre maximum d'itérations
        )
    ],
    style={'padding': '20px','font-family': 'Arial',"textAlign": "center", 'marginTop': '20px'}
    ),
    
    # Cartes avec bouton pour switcher
    dbc.Container([
        dbc.Row([
            dbc.Col(dcc.Graph(figure=carte_emplacement_pvd), width=6),  # Première carte (fixe)

            dbc.Col([
                dcc.Graph(id="graph-switch"),  # Graph dynamique (switch entre dept et regions)
                html.Div(
                html.Button("Carte par régions", 
                            id="switch-button", 
                            n_clicks=0, 
                            className="btn btn-primary",
                            style={"min-width": "230px", "padding": "10px",'backgroundColor': col_bouton,'borderColor': col_bouton}), # Largeur du bouton et couleur
                        style={"textAlign": "right", "margin-right": "10px","margin-top": "10px"}  # Emplacement du bouton
                )
            ])
        ])
        ], fluid=True,style={'padding': '10px'})
    
])



# # 2 Ma petite ville

petite_ville_layout = html.Div([
    # Texte d'explication de la page
    html.P(
        ["Vous pouvez retrouver sur cette page une synthèse des dynamiques démographiques de la commune sélectionnée.", 
         html.Br(),
         html.Br(),
         "Vous pouvez ici analyser quatre graphiques différents : un ",
         html.B("diagramme en barre"), " des naissances et décès ; un ",
         html.B("line chart"), " de l'évolution de la population ; une ",
         html.B("pyramide des âges"), " par sexe ; une ",
         html.B("carte à cases"), " des classes socio-professionnelles.",
         html.Br(),
         html.Br(),
         "Attention, seules les communes membres du programme PVD peuvent être trouvées ; si la communes que vous souhaitez analyser ne se trouve pas dans la barre de recherche, c'est sûrement qu'elle n'en fait pas (encore) partie.",
        ],
        style={'padding': '10px',"textAlign": "left", "margin-left": "10px",'font-size':"16px","margin-bottom":"10px","margin_top":"10px"}),
    
    # Barre de recherche et graphiques liés
    html.Div([
        # Menu de sélection de la ville
        html.B("Commune :",style={"margin-bottom":"10px"}),
        dcc.Dropdown(
        id='dropdown-commune-page-2',  # ID modifié pour la 3ème page
        options=[{'label': commune, 'value': commune} for commune in programme_pvd["lib_com"]],
        value= None,  # Valeur initiale
        placeholder="Sélectionner une commune"
        ),
        
        # Disposition des graphiques en deux colonnes
        html.P(id="output-page-2",style={"margin-top":"10px",'textAlign': 'center'}),
        html.Div([
        html.Div([dcc.Graph(id="naissance-deces-page-2")], style={"width": "49%", "display": "inline-block"}),
        html.Div([dcc.Graph(id="evolution-population-page-2")], style={"width": "49%", "display": "inline-block"})
        ], style={"display": "flex", "justify-content": "space-between", "margin-top": "10px"}),

        html.Div([
        html.Div([dcc.Graph(id="pyramide-page-2")], style={"width": "49%", "display": "inline-block"}),
        html.Div([dcc.Graph(id="treemap-cs-sexe-page-2")], style={"width": "49%", "display": "inline-block"})
        ], style={"display": "flex", "justify-content": "space-between", "margin-top": "20px"}),
    ], style={'padding': '20px', 'font-family': 'Arial'}),
    

    # Bouton information
    dbc.Container([
        
        # Bouton pour ouvrir la pop-up
        html.Div(
            html.Button("Aide à la lecture des graphiques", id="open-info", className="btn btn-primary", n_clicks=0, style={'backgroundColor': col_bouton,'borderColor': col_bouton,'font-size':"18px",'color':'white'}), # Largeur du bouton
            style={"textAlign": "right", "margin-right": "10px","margin-top": "10px"}  # Emplacement du bouton
        ),
                        
        # Modal (pop-up) avec des explications
        dbc.Modal(
            [
            dbc.ModalHeader("Aide à la lecture des graphiques"),
            dbc.ModalBody([
                html.Img(src="assets/graphe_p2_1.jpg", style={"width": "1000px", "height": "auto"}),
                html.Hr(style={"border": "2px dashed black"}),
                html.Img(src="assets/graphe_p2_2.jpg", style={"width": "1000px", "height": "auto"}),
                html.Hr(style={"border": "2px dashed black"}),
                html.Img(src="assets/graphe_p2_p3_1.jpg", style={"width": "1000px", "height": "auto"}),
                html.Hr(style={"border": "2px dashed black"}),
                html.Img(src="assets/graphe_p2_p3_2.jpg", style={"width": "1000px", "height": "auto"}) 
                        ]),
            dbc.ModalFooter(
                dbc.Button("Fermer", id="close-info", className="ml-auto", n_clicks=0, style={'backgroundColor': col_fermeture_bouton_info,'borderColor':col_fermeture_bouton_info,'color':'white'})
            ),
            ],
            id="modal-info",
            is_open=False,  # La pop-up est fermée au début
            size="xl",  # Agrandir la fenêtre
            style={"maxWidth": "90vw", "maxHeight": "90vh"},  # Ajustement manuel si besoin
        )
    ], fluid=True),
    
    # Texte source : INSEE.
    html.P("Source des données : INSEE.", style={"textAlign": "left", "margin-left": "10px"})
    
],)

# Fonction pour le graphique des naissances et des décès
def graphique_naissance_deces(city_data_naiss,city_data_deces,selected_city):
    if city_data_naiss.empty or city_data_deces.empty :
        barplot_naissance_deces = px.scatter(title="Données manquantes sur les naissances et les décès.", height = 500)
    else :
        barplot_naissance_deces = pgo.Figure()
        barplot_naissance_deces.add_trace(pgo.Bar(
                                            x=city_data_naiss["Année"], 
                                            y=city_data_naiss["nb_naissances"],
                                            marker=dict(color=col_naissances), 
                                            name="Naissances", 
                                            opacity=0.8,
                                            hovertemplate =
                                            "<b>Année :</b> %{x} <br>"
                                            "<b>Nombre de naissances :</b> %{y} <br>"
                                            ),
                                        )
        barplot_naissance_deces.add_trace(pgo.Bar(
                                                x=city_data_deces["Année"], 
                                                y=city_data_deces["nb_deces"],
                                                marker=dict(color=col_deces), 
                                                name="Décès", 
                                                opacity=0.8,
                                                hovertemplate =
                                                "<b>Année :</b> %{x} <br>"
                                                "<b>Nombre de décès :</b> %{y} <br>"
                                                ))
        barplot_naissance_deces.update_layout(
                                            title=f"<b>Évolution des naissances et décès à {selected_city}</b>",
                                            xaxis_title="Années", 
                                            yaxis_title="Effectif", 
                                            barmode='group',
                                            plot_bgcolor = col_plot_background,
                                            height = 500,
                                            font_size = 12)
    return barplot_naissance_deces


# Fonction pour le graphique d'évolution de la population
def graphique_linechart_taille_pop(city_data_pop,selected_city):
    if city_data_pop.empty :
        linechart_taille_pop = px.scatter(title="Données manquantes sur l'évolution de la taille de la population.", height = 500)
    else :
        linechart_taille_pop = pgo.Figure()

        linechart_taille_pop.add_scatter(
        x = city_data_pop["Année"],
        y = city_data_pop["Effectif"],
        mode = "lines + markers",
        line = dict(color =col_population, width = 2),
        customdata = city_data_pop[["Année", "Effectif", "Variation"]],
        hovertemplate =
            "<b>Année :</b> %{x} <br>"
            "<b>Population :</b> %{customdata[1]} <br>" 
            "<b>Variation (en %) :</b> %{customdata[2]}<extra></extra>"
        )
        

        linechart_taille_pop.update_layout(title = f"<b>Évolution de la population entre 2006 et 2021 <br>à {selected_city}</b> ",
                                            xaxis_title = "Années",
                                            yaxis_title = "Effectif",
                                            template = 'plotly',
                                            plot_bgcolor = col_plot_background,
                                            height = 500,
                                            font_size = 12
                                            )
    return linechart_taille_pop


# Fonction pour le graphique de pyramide des âges
def graphique_pyramide(city_data_sexe_age,selected_city):
    if city_data_sexe_age.empty :
        pyramide = px.scatter(title="Données manquantes sur l'âge en fonction du sexe.", height = 500)
    else :
        city_data_sexe_age = city_data_sexe_age.sort_values(by = ["Année", "Tranche_age"])
        annees_age = sorted(city_data_sexe_age["Année"].unique())
            # Données initiales (i.e. en 2006)
        annee_initiale = annees_age[0]
        df_annee_age = city_data_sexe_age[city_data_sexe_age["Année"] == annee_initiale]

        ages = df_annee_age["Tranche_age"].unique()

        ages_femmes = list(df_annee_age[df_annee_age["Sexe"] == "F"]["Effectif"])
        ages_hommes = list(df_annee_age[df_annee_age["Sexe"] == "H"]["Effectif"])

        # Calcul des pourcentages
        tot_f = sum(ages_femmes)
        tot_h = sum(ages_hommes)

        ages_femmes_prop = [round((x / tot_f), 4) * 100 for x in ages_femmes]
        ages_hommes_prop = [round((x / tot_h), 4) * 100 for x in ages_hommes]
        ages_hommes_prop_inv = [-x for x in ages_hommes_prop] 
        max_prop = max(max(ages_femmes_prop),max(ages_hommes_prop))
        # Création de la figure
        pyramide = pgo.Figure()

        pyramide.add_trace(pgo.Bar(
                            x = ages_femmes_prop,
                            y = ages,
                            orientation = "h",
                            name = "Femmes",
                            marker = dict(color = col_femme, line = dict(color = "black", width = 0.2)),
                            opacity = 0.8,
                            customdata = ages_femmes,
                            hovertemplate = "<b>Sexe :</b> Femme <br>"
                                            "<b>Tranche d'âge :</b> %{y} ans <br>"
                                            "<b>Effectif :</b> %{customdata} <br>"
                                            "<b>Proportion :</b> %{x} %<extra></extra>"
                        ))

        pyramide.add_trace(pgo.Bar(
                            x = ages_hommes_prop_inv,
                            y = ages,
                            orientation = "h",
                            name = "Hommes",
                            marker = dict(color = col_homme, line = dict(color = "black", width = 0.2)),
                            opacity = 0.8,
                            customdata = pd.DataFrame({"effectif" : ages_hommes,
                                                    "prop" : ages_hommes_prop
                                                    }),
                            hovertemplate =
                                    "<b>Sexe :</b> Homme <br>" 
                                    "<b>Tranche d'âge :</b> %{y} ans <br>"
                                    "<b>Effectif :</b> %{customdata[0]} <br>"
                                    "<b>Proportion :</b> %{customdata[1]} %<extra></extra>"
                            ))

        # Création des frames pour l'animation
        frames = []
        for annee in annees_age :
            df_annee_age = city_data_sexe_age[city_data_sexe_age["Année"] == annee]

            ages_femmes = list(df_annee_age[df_annee_age["Sexe"] == "F"]["Effectif"])
            ages_hommes = list(df_annee_age[df_annee_age["Sexe"] == "H"]["Effectif"])

            tot_f = sum(ages_femmes)
            tot_h = sum(ages_hommes)

            ages_femmes_prop = [round((x / tot_f), 4) * 100 for x in ages_femmes]
            ages_hommes_prop = [round((x / tot_h), 4) * 100 for x in ages_hommes]
            ages_hommes_prop_inv = [-x for x in ages_hommes_prop]

            frames.append(pgo.Frame(
                data = [
                    pgo.Bar(x = ages_femmes_prop, y = ages, orientation = "h"),
                    pgo.Bar(x = ages_hommes_prop_inv, y = ages, orientation = "h")
                ],
                name = str(annee)
            ))

        pyramide.update(frames = frames)

        # Ajout du slider et des boutons de lecture
        pyramide.update_layout(
        sliders = [{
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {"font": {"size": 16}, 
                            "prefix": "Année :",
                            "visible": True,
                            "xanchor": "right"
                            },
            "transition": {"duration": 300, 
                            "easing": "cubic-in-out"
                       },
            "pad": {"b": 10, 
                    "t": 10
                    },
            "len": 0.9,
            "x": 0.1,
            "y": -0.1,
            "steps": [{"args": [[str(annee)], 
                            {"frame": {"duration": 300, "redraw": True}, 
                             "mode": "immediate"}
                            ],
                   "label": str(annee), 
                   "method": "animate"}
                  for annee in annees_age
                  ]
        }],
        title = f"<b>Répartition de la population en fonction de l'âge et du sexe à <br>{selected_city}</b>",
        xaxis_title = "Part de la population (en %)",
        yaxis_title = "Tranches d'âge",
        barmode = 'relative',
        plot_bgcolor = col_plot_background,
        height = 600,
        font_size = 12
        )
    
        pyramide.update_xaxes(range=[-max_prop-5, max_prop+5])
    return pyramide


# Fonction pour le graphique treemap
def graphique_treemap(city_data_cs_sexe,selected_city):
    if city_data_cs_sexe.empty :
        treemap = px.scatter(title="Données manquantes sur la classe socio-profesionnelle.", height = 500)
    else :
        # Listes des classes
        effectif_classes = city_data_cs_sexe.groupby("Classe")["Effectif"].sum().reset_index()

        # Étape 2 : Construire les labels, parents et values    
        labels = list(effectif_classes["Classe"]) + list(city_data_cs_sexe["Sexe"])
        parents = ["Population"] * len(effectif_classes) + list(city_data_cs_sexe["Classe"])
        values = list(effectif_classes["Effectif"]) + list(city_data_cs_sexe["Effectif"])

        labels.insert(0,"Population")
        parents.insert(0,"")
        values.insert(0,city_data_cs_sexe["Effectif"].sum())
        
        df = pd.DataFrame(
            {"labels" : labels,
            "parents" : parents,
            "values" : values
            }    
        )

        # Création d'un dictionnaire des valeurs parentales
        parent_values = {label: value for label, value in zip(df["labels"], df["values"])}

        # Calcul de la part
        df["part"] = df.apply(lambda row: round(row["values"] / parent_values[row["parents"]], 3) * 100
                            if row["parents"] in parent_values and parent_values[row["parents"]] != 0 else 100, axis=1)
        
        # Générer la liste des couleurs dans l'ordre des labels
        colors = [color_dict[label] for label in labels]

        # Création du treemap
        treemap = pgo.Figure(pgo.Treemap(
            labels = labels,
            parents = parents,
            values = values,
            maxdepth = 2, # affiche aucune case sexe sauf si la cs est cliquée
            marker = dict(colors = colors),
            name="",
            customdata = df,
             hovertemplate = "<b>Classe :</b> %{customdata[0]} <br>"
                    "<b>Effectif :</b> %{customdata[2]} <br>"
                    "<b>Proportion :</b> %{customdata[3]} %<extra></extra>"
            ))

        treemap.update_traces(tiling = dict(packing = "squarify"))

        treemap.update_layout(
            title = f"<b>Répartition de la population selon la classe sociale <br>et le sexe à {selected_city} en 2021</b>",
            font_size = 12,
            height = 600,
        )
    return treemap


# # 3 Comparaison de ma petite ville à un territoire

# Possibilités de territoires et critères
territoires = ['Canton', 'Département', 'Région']
criteres = ['Evolution de la taille de la population', 'Age de la population', 'Classes socio-professionnelles de la population']


comparaison_layout = html.Div([
    
    # Texte d'explication de la page
    html.P(
        ["Vous pouvez sur cette page comparer la ville sélectionnée à différents territoires dans lesquels elles s'inscrit. ", 
         "Vous pouvez au choix la comparer à ",
         html.I("son canton, son département"), " ou ",
         html.I("sa région."), 
         html.Br(),
         html.Br(),
         "Chaque territoire peut être comparé selon trois aspects : ",
         html.I("évolution de la taille de la population"), " ; ",
         html.I("âge de la population"), " ; ",
         html.I("classes socio-professionnelles"), ".", 
         html.Br(),
         html.Br(),
         "Suivant votre choix de comparaison, vous pourrez voir les graphiques suivants : des ",
         html.B("diagramme en barre"), " des naissances et décès et un ",
         html.B("line chart"), " de l'évolution de la population ; des ",
         html.B("pyramides des âges"), " par sexe et un ",
         html.B("diagrammes en barre"), " par tranche d'âge ; des ",
         html.B("cartes à cases"), " des classes socio-professionnelles."
        ], 
        style={'padding': '10px',"textAlign": "left", "margin-left": "10px",'font-size':"16px","margin-bottom":"10px","margin_top":"10px"}),
    
    # Menus déroulant pour la sélection de la commune, du territoire et du critère de comparaison
    html.Div([
        # Menu de sélection de la commune
        html.B("Commune :",style={"margin-bottom":"10px"}),
        dcc.Dropdown(
        id='dropdown-commune-page-3',  # ID modifié pour la 3ème page
        options=[{'label': commune, 'value': commune} for commune in programme_pvd["lib_com"]],
        value=None,  # Valeur initiale
        placeholder="Sélectionner une commune",
        style={"margin-bottom":"10px"}
        ),
        # Menu déroulant pour choisir le territoire
        html.B("Territoire :",style={"margin-bottom":"10px"}),
        dcc.Dropdown(
        id='dropdown-territoire-page-3',  # ID modifié pour la 3ème page
        options=[{'label': territoire, 'value': territoire} for territoire in territoires],
        value=None,  # Valeur initiale
        placeholder="Sélectionner un territoire",
        style={"margin-bottom":"10px"}
        ),
        # Menu déroulant pour choisir le critere
        html.B("Critère de sélection :",style={"margin-bottom":"10px"}),
        dcc.Dropdown(
        id='dropdown-critere-page-3',  # ID modifié pour la 3ème page
        options=[{'label': critere, 'value': critere} for critere in criteres],
        value=None,  # Valeur initiale
        placeholder="Sélectionner un critère de comparaison",
        style={"margin-bottom":"10px"}
        ),
        
        # Zone pour afficher les valeurs sélectionnées
        html.Div(id='output-page-3',style={"margin-top":"10px","textAlign":"center"})
    ], style={'padding': '20px', 'font-family': 'Arial'}),
    

     # Bouton information
    dbc.Container([
        
        # Bouton pour ouvrir la pop-up
        html.Div(
            html.Button("Aide à la lecture des graphiques", id="open-info", className="btn btn-primary", n_clicks=0, style={'backgroundColor': col_bouton,'borderColor': col_bouton,'font-size':"18px",'color':'white'}), # Largeur du bouton
            style={"textAlign": "right", "margin-right": "10px","margin-top": "10px"}  # Emplacement du bouton
        ),
                        
        # Modal (pop-up) avec des explications
        dbc.Modal(
            [
            dbc.ModalHeader("Aide à la lecture des graphiques"),
            dbc.ModalBody([
                html.Img(src="assets/graphe_p3_1.jpg", style={"width": "1000px", "height": "auto"}),
                html.Hr(style={"border": "2px dashed black"}),
                html.Img(src="assets/graphe_p3_2.jpg", style={"width": "1000px", "height": "auto"}),
                html.Hr(style={"border": "2px dashed black"}),
                html.Img(src="assets/graphe_p2_p3_1.jpg", style={"width": "1000px", "height": "auto"}),
                html.Hr(style={"border": "2px dashed black"}),
                html.Img(src="assets/graphe_p3_3.jpg", style={"width": "1000px", "height": "auto"}),
                html.Hr(style={"border": "2px dashed black"}),
                html.Img(src="assets/graphe_p2_p3_2.jpg", style={"width": "1000px", "height": "auto"})   
                        ]),
            dbc.ModalFooter(
                dbc.Button("Fermer", id="close-info", className="ml-auto", n_clicks=0, style={'backgroundColor': col_fermeture_bouton_info,'borderColor':col_fermeture_bouton_info,'color':'white'})
            ),
            ],
            id="modal-info",
            is_open=False,  # La pop-up est fermée au début
            size="xl",  # Agrandir la fenêtre
            style={"maxWidth": "90vw", "maxHeight": "90vh"},  # Ajustement manuel si besoin
        )
    ], fluid=True),
    
    
    # Texte source : INSEE.
    html.P("Source des données : INSEE.", style={"textAlign": "left", "margin-left": "10px"})
    
])


# Récupération des cartes

def carte_comcom(selected_city):
    insee_selected = donnees_communes[donnees_communes["Commune"] == selected_city]["insee_com"].values[0]

    dep_selected = donnees_communes[donnees_communes["Commune"] == selected_city]["Département"].values[0]
    comcom_selected = donnees_communes[donnees_communes["Commune"] == selected_city]["Communauté de commune"].values[0]
    liste_insee_com_dans_comcom = donnees_communes[
        (donnees_communes["Communauté de commune"] == comcom_selected) & 
        (donnees_communes["Département"] == dep_selected)
        ]["insee_com"].values

    # Filtrer les contours des communes de la communauté de communes
    contours_des_communes_comcom = contours_des_communes[contours_des_communes["codgeo"].isin(liste_insee_com_dans_comcom)]

    # Ajouter une colonne catégorielle pour la couleur
    contours_des_communes_comcom["color_category"] = contours_des_communes_comcom["codgeo"].apply(
        lambda x: "Commune sélectionnée" if x == insee_selected else "Autres communes"
    )

    # Récupérer les coordonnées pour centrer la carte
    lat_commune = programme_pvd[programme_pvd["insee_com"] == insee_selected]["lat"].values[0]
    long_commune = programme_pvd[programme_pvd["insee_com"] == insee_selected]["long"].values[0]

    # Carte
    carte_comcom = px.choropleth_mapbox(
        contours_des_communes_comcom,
        geojson=contours_des_communes_comcom["geometry"],
        locations=contours_des_communes_comcom.index,
        color="color_category",  # Utilisation de la catégorie pour la couleur
        mapbox_style="carto-positron",
        zoom=8.2, 
        center={'lat': lat_commune, 'lon': long_commune},  
        opacity=0.8,  
        title=f"<b>Emplacement de {selected_city} dans son canton</b>",
        custom_data=["libgeo", "codgeo"],
        labels={"color_category":"Type de commune"},
        color_discrete_map={"Commune sélectionnée": col_commune, "Autres communes": col_territoire},  # Définition des couleurs fixes
        height=500,
    )

    # Personnalisation de l'affichage au survol
    carte_comcom.update_traces(
        hovertemplate="<br>".join([
            "<b>Nom :</b> %{customdata[0]}",
            "<b>Code INSEE :</b> %{customdata[1]}"
        ]),
        marker_line_width=1,
        marker_line_color=col_contours
    )

    return carte_comcom

def carte_departement(selected_city):
    insee_selected = donnees_communes[donnees_communes["Commune"] == selected_city]["insee_com"].values[0]

    # Identifier le département de la ville sélectionnée
    dep_selected = donnees_communes[donnees_communes["Commune"] == selected_city]["Département"].values[0]
    dep_nom = programme_pvd[programme_pvd["lib_com"]==selected_city]["Nom Officiel Département"].values[0]

    # Filtrer les contours des communes du département
    contours_des_communes_departement = contours_des_communes[contours_des_communes["dep"] == dep_selected]

    # Ajouter une colonne catégorielle pour la couleur
    contours_des_communes_departement["color_category"] = contours_des_communes_departement["codgeo"].apply(
        lambda x: "Commune sélectionnée" if x == insee_selected else "Autres communes"
    )

    # Coordonnées pour centrer la carte
    lat_commune = programme_pvd[programme_pvd["insee_com"] == insee_selected]["lat"].values[0]
    long_commune = programme_pvd[programme_pvd["insee_com"] == insee_selected]["long"].values[0]

    # Carte 
    carte_departement = px.choropleth_mapbox(
        contours_des_communes_departement,
        geojson=contours_des_communes_departement["geometry"],
        locations=contours_des_communes_departement.index,
        color="color_category",  # Utilisation de la catégorie pour la couleur
        mapbox_style="carto-positron",
        zoom=6.5,  # Zoom ajusté pour afficher le département entier
        center={'lat': lat_commune, 'lon': long_commune},  
        opacity=0.8,  
        title=f"<b>Emplacement de {selected_city} dans son département <br> ({dep_nom})</b>",
        labels={"color_category":"Type de commune"},
        custom_data=["libgeo", "codgeo"],
        color_discrete_map={"Commune sélectionnée": col_commune, "Autres communes": col_territoire},  # Définition des couleurs fixes
        height=500
    )

    # Personnalisation de l'affichage au survol
    carte_departement.update_traces(
        hovertemplate="<br>".join([
            "<b>Nom :</b> %{customdata[0]}",
            "<b>Code INSEE :</b> %{customdata[1]}"
        ]),
        marker_line_width=1,
        marker_line_color=col_contours
    )
    return carte_departement


def carte_region(selected_city):
    insee_selected = donnees_communes[donnees_communes["Commune"] == selected_city]["insee_com"].values[0]

    # Identifier la région de la ville sélectionnée
    reg_selected = donnees_communes[donnees_communes["Commune"] == selected_city]["REG"].values[0]
    reg_nom = programme_pvd[programme_pvd["lib_com"] == selected_city]["Nom Officiel Région"].values[0]

    # Filtrer les contours des communes de la région
    contours_des_communes_region = contours_des_communes[contours_des_communes["reg"] == str(reg_selected)]

    # Ajouter une colonne catégorielle pour la couleur
    contours_des_communes_region["color_category"] = contours_des_communes_region["codgeo"].apply(
    lambda x: "Commune sélectionnée" if x == insee_selected else "Autres communes"
    )

    # Cordonnées de la ville sélectionnée
    lat_commune = programme_pvd[programme_pvd["insee_com"] == insee_selected]["lat"].values[0]
    long_commune = programme_pvd[programme_pvd["insee_com"] == insee_selected]["long"].values[0]

    carte_region = px.choropleth_mapbox(
    contours_des_communes_region,
    geojson=contours_des_communes_region["geometry"],
    locations=contours_des_communes_region.index,
    color="color_category",  # Utilisation de la catégorie pour la couleur
    mapbox_style="carto-positron",
    zoom=5.5,  # Zoom plus large pour voir la région entière
    center={'lat': lat_commune, 'lon': long_commune},  
    opacity=0.8,  
    title=f"<b>Emplacement de {selected_city} dans sa région <br> ({reg_nom})</b>",
    labels={"color_category":"Type de commune"},
    custom_data=["libgeo", "codgeo"],
    color_discrete_map={"Commune sélectionnée": col_commune, "Autres communes": col_territoire},  # Définition des couleurs fixes
    height=500
    )

    # Personnalisation de l'affichage au survol
    carte_region.update_traces(
    hovertemplate="<br>".join([
        "<b>Nom :</b> %{customdata[0]}",
        "<b>Code INSEE :</b> %{customdata[1]}"
    ]),
    marker_line_width=1,
    marker_line_color=col_contours
    )

    return carte_region


# Récupération des noms des départements et des régions


def recup_nom_territoire(selected_city,territoire_selected):
    if territoire_selected == "Département":
        return programme_pvd[programme_pvd["lib_com"] == selected_city]["Nom Officiel Département"].values[0]
    else :
        return programme_pvd[programme_pvd["lib_com"] == selected_city]["Nom Officiel Région"].values[0]


# Fonctions pour faire les graphiques

# Fonction pour les graphes sur la taille de la population
def graphiques_taille_pop(selected_city,territoire_selected):
    
    insee_selected = programme_pvd[programme_pvd["lib_com"] == selected_city]["insee_com"].values[0]
    
    city_data_naiss = naissances[naissances["insee_com"] == insee_selected]
    city_data_naiss = city_data_naiss.sort_values(by = "Année") 
    
    city_data_deces = deces[deces["insee_com"] == insee_selected]
    city_data_deces = city_data_deces.sort_values(by = "Année")
    
    city_data_pop = data_age_population_generale[(data_age_population_generale["insee_com"] == insee_selected) & (data_age_population_generale["Tranche_age"] == "Total")]
    city_data_pop = city_data_pop.sort_values(by = "Année")   # pour être sûr de l'ordre
    city_data_pop["Variation"] = round(city_data_pop["Effectif"].pct_change() * 100, 2)
    city_data_pop.fillna(0, inplace = True)
    

    if territoire_selected == "Canton" :
        dep_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Département"].values[0]
        comcom_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Communauté de commune"].values[0]
        
        comcom_data_deces = deces[(deces["Communauté de commune"] == comcom_selected) & (deces["Département"] == dep_selected)]
        comcom_data_deces = comcom_data_deces.groupby(["Année", "Communauté de commune", "Département"], as_index = False)[["nb_deces", "Effectif"]].sum()
        comcom_data_deces = comcom_data_deces.sort_values(by = "Année") 
        
        comcom_data_naiss = naissances[(naissances["Communauté de commune"] == comcom_selected) & (naissances["Département"] == dep_selected)]
        comcom_data_naiss = comcom_data_naiss.groupby(["Année", "Communauté de commune", "Département"], as_index = False)[["nb_naissances", "Effectif"]].sum()
        comcom_data_naiss = comcom_data_naiss.sort_values(by = "Année") 
        
        comcom_data_pop = data_age_population_generale[data_age_population_generale["Communauté de commune"] == comcom_selected]
        comcom_data_pop = comcom_data_pop[comcom_data_pop["Département"] == dep_selected]
        comcom_data_pop = comcom_data_pop[comcom_data_pop["Tranche_age"] == "Total"]
        comcom_data_pop = comcom_data_pop.groupby(["Année", "Communauté de commune", "Département"], as_index = False).sum("Effectif")
        comcom_data_pop = comcom_data_pop.sort_values(by = "Année")   # pour être sûr de l'ordre
        comcom_data_pop["Variation"] = round(comcom_data_pop["Effectif"].pct_change() * 100, 2)
        comcom_data_pop.fillna(0, inplace = True)
        
        terr_data_naiss = comcom_data_naiss
        terr_data_deces = comcom_data_deces
        terr_data_pop = comcom_data_pop
        
        
    elif territoire_selected == "Département" :
        dep_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Département"].values[0]
        
        dep_data_deces = deces[naissances["Département"] == dep_selected]
        dep_data_deces = dep_data_deces.groupby(["Année", "Département"], as_index = False)[["nb_deces", "Effectif"]].sum()
        dep_data_deces = dep_data_deces.sort_values(by = "Année") 
        
        dep_data_naiss = naissances[naissances["Département"] == dep_selected]
        dep_data_naiss = dep_data_naiss.groupby(["Année", "Département"], as_index = False)[["nb_naissances", "Effectif"]].sum()
        dep_data_naiss = dep_data_naiss.sort_values(by = "Année") 
        
        dep_data_pop = data_age_population_generale[data_age_population_generale["Département"] == dep_selected]
        dep_data_pop = dep_data_pop[dep_data_pop["Tranche_age"] == "Total"]
        dep_data_pop = dep_data_pop.groupby(["Année", "Département"], as_index = False).sum("Effectif")
        dep_data_pop = dep_data_pop.sort_values(by = "Année")   # pour être sûr de l'ordre
        dep_data_pop["Variation"] = round(dep_data_pop["Effectif"].pct_change() * 100, 2)
        dep_data_pop.fillna(0, inplace = True)
        
        terr_data_naiss = dep_data_naiss
        terr_data_deces = dep_data_deces
        terr_data_pop = dep_data_pop
        
        
    else :
        reg_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Région"].values[0]
        
        reg_data_deces = deces[deces["Région"] == reg_selected]
        reg_data_deces = reg_data_deces.groupby(["Année", "Région"], as_index = False)[["nb_deces", "Effectif"]].sum()
        reg_data_deces = reg_data_deces.sort_values(by = "Année") 
        
        reg_data_naiss = naissances[naissances["Région"] == reg_selected]
        reg_data_naiss = reg_data_naiss.groupby(["Année", "Région"], as_index = False)[["nb_naissances", "Effectif"]].sum()
        reg_data_naiss = reg_data_naiss.sort_values(by = "Année")
        
        reg_data_pop = data_age_population_generale[data_age_population_generale["Région"] == reg_selected]
        reg_data_pop = reg_data_pop[reg_data_pop["Tranche_age"] == "Total"]
        reg_data_pop = reg_data_pop.groupby(["Année", "Région"], as_index = False).sum("Effectif")
        reg_data_pop = reg_data_pop.sort_values(by = "Année")   # pour être sûr de l'ordre
        reg_data_pop["Variation"] = round(reg_data_pop["Effectif"].pct_change() * 100, 2)
        reg_data_pop.fillna(0, inplace = True)
        
        terr_data_naiss = reg_data_naiss
        terr_data_deces = reg_data_deces
        terr_data_pop = reg_data_pop

    territoire_name = ""
    if territoire_selected == "Canton":
        territoire_name = "comparé à son canton"
    else :
        territoire_name = "et en " + recup_nom_territoire(selected_city,territoire_selected)

    # 1 Graphique des naissances
    fig311 = pgo.Figure()
    fig311.add_trace(
    pgo.Bar(
        x = city_data_naiss["Année"], 
        y = city_data_naiss['nb_naissances'] / city_data_naiss['Effectif'] * 100,
        marker = dict(color = col_naissances),
        name = f"{selected_city}",
        opacity = 0.8,
        customdata = city_data_naiss[['Année', 'nb_naissances']],
        hovertemplate =
            "<b>Année :</b> %{x} <br>" 
            "<b>Nombre de naissances :</b> %{customdata[1]} <extra></extra>"
        )
    )
    fig311.add_trace(
    pgo.Bar(
        x = terr_data_naiss["Année"], 
        y = terr_data_naiss['nb_naissances'] / terr_data_naiss['Effectif'] * 100,
        marker = dict(color = col_naissances_darker),
        name = f"{territoire_selected}",
        opacity = 0.8,
        customdata = terr_data_naiss[['Année', 'nb_naissances']],
        hovertemplate =
            "<b>Année :</b> %{x} <br>" 
            "<b>Nombre de naissances :</b> %{customdata[1]} <extra></extra>"
        )
    )
    fig311.update_layout(
    title = f"Évolution des <b>naissances</b> à {selected_city} <br>{territoire_name}",
    xaxis_title = "Années",
    yaxis_title = "Nombre de naissances pour 100 habitants",
    barmode = 'group',
    template = 'plotly',
    plot_bgcolor = col_plot_background,
    height = 500
    )
    
    # 2 Graphique des décès
    fig312 = pgo.Figure()
    fig312.add_trace(
    pgo.Bar(
        x = city_data_deces["Année"], 
        y = city_data_deces['nb_deces'] / city_data_deces['Effectif'] * 100,
        marker = dict(color = col_deces),
        name = f"{selected_city}",
        opacity = 0.8,
        customdata = city_data_deces[['Année', 'nb_deces']],
        hovertemplate =
            "<b>Année :</b> %{x} <br>" 
            "<b>Nombre de décès :</b> %{customdata[1]} <extra></extra>"
        )
    )
    fig312.add_trace(
    pgo.Bar(
        x = terr_data_deces["Année"], 
        y = terr_data_deces['nb_deces'] / terr_data_deces['Effectif'] * 100,
        marker = dict(color = col_deces_darker),
        name = f"{territoire_selected}",
        opacity = 0.8,
        customdata = terr_data_deces[['Année', 'nb_deces']],
        hovertemplate =
            "<b>Année :</b> %{x} <br>" 
            "<b>Nombre de décès :</b> %{customdata[1]} <extra></extra>"
        )
    )
    fig312.update_layout(title = f"Évolution des <b>décès</b> à {selected_city} <br>{territoire_name}",
                  xaxis_title = "Années",
                  yaxis_title = "Nombre de décès pour 100 habitants",
                  barmode = 'group',
                  template = 'plotly',
                  plot_bgcolor = col_plot_background,
                  height = 500
              )
    
    
    # 3 Variation de la population
    fig313 = pgo.Figure()

    fig313.add_scatter(
    x = city_data_pop["Année"],
    y = city_data_pop["Variation"],
    name = f"{selected_city}",
    mode = "lines + markers",
    line = dict(color = col_population, width = 2),
    customdata = city_data_pop[["Année", "Effectif", "Variation"]],
    hovertemplate =
        "<b>Année :</b> %{x} <br>"
        "<b>Population :</b> %{customdata[1]} <br>" 
        "<b>Variation (en %) :</b> %{customdata[2]}<extra></extra>"
    )

    fig313.add_scatter(
    x = terr_data_pop["Année"],
    y = terr_data_pop["Variation"],
    name = f"{territoire_selected}",
    mode = "lines + markers",
    line = dict(color = col_population_darker, width = 2),
    customdata = terr_data_pop[["Année", "Effectif", "Variation"]],
    hovertemplate =
        "<b>Année :</b> %{x} <br>"
        "<b>Population :</b> %{customdata[1]} <br>" 
        "<b>Variation (en %) :</b> %{customdata[2]}<extra></extra>"
    )

    fig313.update_layout(title = f"Évolution de la <b>population</b> à {selected_city} <br>{territoire_name}",
                  xaxis_title = "Années",
                  yaxis_title = f"Variation de la population par <br>rapport à l'année précédente (en %)",
                  template = 'plotly',
                  plot_bgcolor = col_plot_background,
                  height = 500
              )
    
    # carte
    if territoire_selected == "Canton":
        carte = carte_comcom(selected_city)
    elif territoire_selected == "Département":
        carte = carte_departement(selected_city)
    else :
        carte = carte_region(selected_city)
    
    return html.Div([
        html.Div([
        html.Div([dcc.Graph(figure=fig311)], style={"width": "49%", "display": "inline-block"}),
        html.Div([dcc.Graph(figure=fig312)], style={"width": "49%", "display": "inline-block"})
        ], style={"display": "flex", "justify-content": "space-between", "margin-top": "10px"}
                 ),
        html.Div([
        html.Div([dcc.Graph(figure=fig313)], style={"width": "49%", "display": "inline-block"}),
        html.Div([dcc.Graph(figure=carte)], style={"width": "49%", "display": "inline-block"})
        ], style={"display": "flex", "justify-content": "space-between", "margin-top": "20px"})
        ])
    


# Fonction pour les graphes sur l'âge de la population
def graphiques_age_pop(selected_city,territoire_selected):
    insee_selected = programme_pvd[programme_pvd["lib_com"] == selected_city]["insee_com"].values[0]
    
    territoire_name = ""
    if territoire_selected == "Canton":
        territoire_name = "comparé à son canton"
    else :
        territoire_name = "et en " + recup_nom_territoire(selected_city,territoire_selected)

    territoire_name2 = ""
    if territoire_selected == "Canton":
        territoire_name2 = "dans le canton"
    else :
        territoire_name2 = "en " + recup_nom_territoire(selected_city,territoire_selected)
        
    # Données filtrées pour la ville
    city_data_sexe_age = data_age_selon_sexe[data_age_selon_sexe["insee_com"] == insee_selected]
    city_data_sexe_age = city_data_sexe_age.sort_values(by = ["Année", "Tranche_age"])
    # Années disponibles
    annees_age = sorted(city_data_sexe_age["Année"].unique())
    # Données initiales (i.e. en 2006)
    annee_initiale = annees_age[0]
    df_annee_age = city_data_sexe_age[city_data_sexe_age["Année"] == annee_initiale]
    ages = df_annee_age["Tranche_age"].unique()
    ages_femmes = list(df_annee_age[df_annee_age["Sexe"] == "F"]["Effectif"])
    ages_hommes = list(df_annee_age[df_annee_age["Sexe"] == "H"]["Effectif"])
    # Calcul des pourcentages
    tot_f = sum(ages_femmes)
    tot_h = sum(ages_hommes)
    ages_femmes_prop = [round((x / tot_f), 4) * 100 for x in ages_femmes]
    ages_hommes_prop = [round((x / tot_h), 4) * 100 for x in ages_hommes]
    ages_hommes_prop_inv = [-x for x in ages_hommes_prop] 
    max_prop = max(max(ages_femmes_prop),max(ages_hommes_prop))
    
    
    # 1. Pyramide des âges pvd
    fig321 = pgo.Figure()

    fig321.add_trace(pgo.Bar(
    x = ages_femmes_prop,
    y = ages,
    orientation = "h",
    name = "Femmes",
    marker = dict(color = col_femme, line = dict(color = "black", width = 0.2)),
    opacity = 0.8,
    customdata = ages_femmes,
    hovertemplate = "<b>Sexe :</b> Femme <br>"
                    "<b>Tranche d'âge :</b> %{y} ans <br>"
                    "<b>Effectif :</b> %{customdata} <br>"
                    "<b>Proportion :</b> %{x} %<extra></extra>"
    ))

    fig321.add_trace(pgo.Bar(
    x = ages_hommes_prop_inv,
    y = ages,
    orientation = "h",
    name = "Hommes",
    marker = dict(color = col_homme, line = dict(color = "black", width = 0.2)),
    opacity = 0.8,
    customdata = pd.DataFrame({"effectif" : ages_hommes,
                               "prop" : ages_hommes_prop
                               }),
    hovertemplate =
        "<b>Sexe :</b> Homme <br>" 
        "<b>Tranche d'âge :</b> %{y} ans <br>"
        "<b>Effectif :<b> %{customdata[0]} <br>"
        "<b>Proportion :</b> %{customdata[1]} %<extra></extra>"
    ))

    # Création des frames pour l'animation
    frames = []
    for annee in annees_age :
        df_annee_age = city_data_sexe_age[city_data_sexe_age["Année"] == annee]

        ages_femmes = list(df_annee_age[df_annee_age["Sexe"] == "F"]["Effectif"])
        ages_hommes = list(df_annee_age[df_annee_age["Sexe"] == "H"]["Effectif"])

        tot_f = sum(ages_femmes)
        tot_h = sum(ages_hommes)

        ages_femmes_prop = [round((x / tot_f), 4) * 100 for x in ages_femmes]
        ages_hommes_prop = [round((x / tot_h), 4) * 100 for x in ages_hommes]
        ages_hommes_prop_inv = [-x for x in ages_hommes_prop]

        frames.append(pgo.Frame(
            data = [
                pgo.Bar(x = ages_femmes_prop, y = ages, orientation = "h"),
                pgo.Bar(x = ages_hommes_prop_inv, y = ages, orientation = "h")
            ],
            name = str(annee)
        ))

    fig321.update(frames = frames)

    # Ajout du slider et des boutons de lecture
    fig321.update_layout(
    sliders = [{
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {"font": {"size": 16}, 
                         "prefix": "Année :",
                         "visible": True,
                         "xanchor": "right"
                         },
        "transition": {"duration": 300, 
                       "easing": "cubic-in-out"
                       },
        "pad": {"b": 10, 
                "t": 10
                },
        "len": 0.9,
        "x": 0.1,
        "y": -0.1,
        "steps": [{"args": [[str(annee)], 
                            {"frame": {"duration": 300, "redraw": True}, 
                             "mode": "immediate"}
                            ],
                   "label": str(annee), 
                   "method": "animate"}
                  for annee in annees_age
                  ]
    }],
    title = f"Répartition de la population en fonction de <b>l'âge et du sexe </b><br>à {selected_city}",
    xaxis_title = "Part de la population concernée (en %)",
    yaxis_title = "Tranches d'âge",
    barmode = 'relative',
    plot_bgcolor = col_plot_background,
    height = 500
    )
    
    fig321.update_xaxes(range=[-max_prop-5, max_prop+5])

    
    # Récupération des données selon le territoire

    if territoire_selected == "Canton" :
        comcom_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Communauté de commune"].values[0]
        dep_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Département"].values[0]
        
        comcom_data_sexe_age = data_age_selon_sexe[data_age_selon_sexe["Communauté de commune"] == comcom_selected]
        comcom_data_sexe_age = comcom_data_sexe_age[comcom_data_sexe_age["Département"] == dep_selected]
        comcom_data_sexe_age = comcom_data_sexe_age.groupby(["Année", "Communauté de commune", "Sexe", "Tranche_age"], as_index = False).sum("Effectif")
        comcom_data_sexe_age = comcom_data_sexe_age.sort_values(by = ["Année", "Tranche_age"])   # pour être sûr de l'ordre

        comcom_data_pop_age = data_age_selon_sexe[data_age_selon_sexe["Communauté de commune"] == comcom_selected]
        comcom_data_pop_age = comcom_data_pop_age[comcom_data_pop_age["Département"] == dep_selected]
        comcom_data_pop_age = comcom_data_pop_age.groupby(["Année", "Communauté de commune", "Tranche_age"], as_index = False)[["Effectif"]].sum()
        comcom_data_pop_age = comcom_data_pop_age.sort_values(by = ["Année", "Tranche_age"])


        terr_data_sexe_age = comcom_data_sexe_age
        terr_data_pop_age = comcom_data_pop_age
    elif territoire_selected == "Département" :
        dep_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Département"].values[0]
        
        dep_data_sexe_age = data_age_selon_sexe[data_age_selon_sexe["Département"] == dep_selected]
        dep_data_sexe_age = dep_data_sexe_age.groupby(["Année", "Département", "Sexe", "Tranche_age"], as_index = False).sum("Effectif")
        dep_data_sexe_age = dep_data_sexe_age.sort_values(by = ["Année", "Tranche_age"])

        dep_data_pop_age = data_age_selon_sexe[data_age_selon_sexe["Département"] == dep_selected]
        dep_data_pop_age = dep_data_pop_age.groupby(["Année", "Département", "Tranche_age"], as_index = False)[["Effectif"]].sum()
        dep_data_pop_age = dep_data_pop_age.sort_values(by = ["Année", "Tranche_age"])

        terr_data_sexe_age = dep_data_sexe_age
        terr_data_pop_age = dep_data_pop_age
    else :
        reg_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Région"].values[0]
        
        reg_data_sexe_age = data_age_selon_sexe[data_age_selon_sexe["Région"] == reg_selected]
        reg_data_sexe_age = reg_data_sexe_age.groupby(["Année", "Région", "Sexe", "Tranche_age"], as_index = False).sum("Effectif")
        reg_data_sexe_age = reg_data_sexe_age.sort_values(by = ["Année", "Tranche_age"])

        reg_data_pop_age = data_age_selon_sexe[data_age_selon_sexe["Région"] == reg_selected]
        reg_data_pop_age = reg_data_pop_age.groupby(["Année", "Région", "Tranche_age"], as_index = False)[["Effectif"]].sum()
        reg_data_pop_age = reg_data_pop_age.sort_values(by = ["Année", "Tranche_age"])


        terr_data_sexe_age = reg_data_sexe_age
        terr_data_pop_age = reg_data_pop_age

    
    # 2 Pyramide des âges terrtitoire
    
    df_annee_age = terr_data_sexe_age[terr_data_sexe_age["Année"] == annee_initiale]
    ages = df_annee_age["Tranche_age"].unique()
    ages_femmes = list(df_annee_age[df_annee_age["Sexe"] == "F"]["Effectif"])
    ages_hommes = list(df_annee_age[df_annee_age["Sexe"] == "H"]["Effectif"])
    # Calcul des pourcentages
    tot_f = sum(ages_femmes)
    tot_h = sum(ages_hommes)
    ages_femmes_prop = [round((x / tot_f), 4) * 100 for x in ages_femmes]
    ages_hommes_prop = [round((x / tot_h), 4) * 100 for x in ages_hommes]
    ages_hommes_prop_inv = [-x for x in ages_hommes_prop] 
    max_prop = max(max(ages_femmes_prop), max(ages_hommes_prop))
        
    fig322 = pgo.Figure()

    fig322.add_trace(pgo.Bar(
    x = ages_femmes_prop,
    y = ages,
    orientation = "h",
    name = "Femmes",
    marker = dict(color = col_femme, line = dict(color = "black", width = 0.2)),
    opacity = 0.8,
    customdata = ages_femmes,
    hovertemplate = "<b>Sexe :</b> Femme <br>"
                    "<b>Tranche d'âge :</b> %{y} ans <br>"
                    "<b>Effectif :</b> %{customdata} <br>"
                    "<b>Proportion :</b> %{x} %<extra></extra>"
    ))

    fig322.add_trace(pgo.Bar(
    x = ages_hommes_prop_inv,
    y = ages,
    orientation = "h",
    name = "Hommes",
    marker = dict(color = col_homme, line = dict(color = "black", width = 0.2)),
    opacity = 0.8,
    customdata = pd.DataFrame({"effectif" : ages_hommes,
                               "prop" : ages_hommes_prop
                               }),
    hovertemplate =
        "<b>Sexe :</b> Homme <br>" 
        "<b>Tranche d'âge :</b> %{y} ans <br>"
        "<b>Effectif :<b> %{customdata[0]} <br>"
        "<b>Proportion :</b> %{customdata[1]} %<extra></extra>"
    ))

    # Création des frames pour l'animation
    frames = []
    for annee in annees_age :
        df_annee_age = terr_data_sexe_age[terr_data_sexe_age["Année"] == annee]

        ages_femmes = list(df_annee_age[df_annee_age["Sexe"] == "F"]["Effectif"])
        ages_hommes = list(df_annee_age[df_annee_age["Sexe"] == "H"]["Effectif"])

        tot_f = sum(ages_femmes)
        tot_h = sum(ages_hommes)

        ages_femmes_prop = [round((x / tot_f), 4) * 100 for x in ages_femmes]
        ages_hommes_prop = [round((x / tot_h), 4) * 100 for x in ages_hommes]
        ages_hommes_prop_inv = [-x for x in ages_hommes_prop]

        frames.append(pgo.Frame(
        data = [
            pgo.Bar(x = ages_femmes_prop, y = ages, orientation = "h"),
            pgo.Bar(x = ages_hommes_prop_inv, y = ages, orientation = "h")
        ],
        name = str(annee)
        ))

    fig322.update(frames = frames)

    # Ajout du slider et des boutons de lecture
    fig322.update_layout(
    sliders = [{
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {"font": {"size": 16}, 
                         "prefix": "Année :",
                         "visible": True,
                         "xanchor": "right"
                         },
        "transition": {"duration": 300, 
                       "easing": "cubic-in-out"
                       },
        "pad": {"b": 10, 
                "t": 10
                },
        "len": 0.9,
        "x": 0.1,
        "y": -0.1,
        "steps": [{"args": [[str(annee)], 
                            {"frame": {"duration": 300, "redraw": True}, 
                             "mode": "immediate"}
                            ],
                   "label": str(annee), 
                   "method": "animate"}
                  for annee in annees_age
                  ]
    }],
    title = f"Répartition de la population en fonction de <b>l'âge et du sexe</b> <br>{territoire_name2}",
    xaxis_title = "Part de la population concernée (en %)",
    yaxis_title = "Tranches d'âge",
    barmode = 'relative',
    template = 'plotly',
    plot_bgcolor = col_plot_background,
    height = 500
    )
    fig322.update_xaxes(range=[-max_prop-5, max_prop+5])
    
    # 3 Barplot des âges 

    city_data_pop_age = data_age_selon_sexe[data_age_selon_sexe["insee_com"] == insee_selected]
    city_data_pop_age = city_data_pop_age.groupby(["Année", "insee_com", "Tranche_age"], as_index = False)[["Effectif"]].sum()
    city_data_pop_age = city_data_pop_age.sort_values(by = ["Année", "Tranche_age"])

    
    annees_age = sorted(city_data_pop_age["Année"].unique())
    annee_initiale = annees_age[0]
    df_pvd = city_data_pop_age[city_data_pop_age["Année"] == annee_initiale]
    df_terr = terr_data_pop_age[terr_data_pop_age["Année"] == annee_initiale]
    ages = df_pvd["Tranche_age"].unique()

    tot_pvd = sum(df_pvd["Effectif"])
    tot_terr = sum(df_terr["Effectif"])

    ages_pvd_prop = [round((x / tot_pvd), 4) * 100 for x in df_pvd["Effectif"]]
    ages_terr_prop = [round((x / tot_terr), 4) * 100 for x in df_terr["Effectif"]]


    fig323 = pgo.Figure()

    fig323.add_trace(
    pgo.Bar(
        x = ages,
        y = ages_pvd_prop,
        marker = dict(color = col_population, line = dict(color = "black", width = 0.2)),
        name = f"{selected_city}",
        opacity = 0.8,
        customdata = df_pvd["Effectif"],
        hovertemplate = 
            "<b>Tranche d'âge :</b> %{x} ans <br>"
            "<b>Effectif :</b> %{customdata} <br>"
            "<b>Propotion :</b> %{y} %<extra></extra>"
    )
    )

    fig323.add_trace(
    pgo.Bar(
        x = ages,
        y = ages_terr_prop,
        marker = dict(color = col_population_darker, line = dict(color = "black", width = 0.2)),
        name = f"{territoire_selected}",
        opacity = 0.8,
        customdata = df_terr["Effectif"],
        hovertemplate = 
            "<b>Tranche d'âge :</b> %{x} ans <br>"
            "<b>Effectif :</b> %{customdata} <br>"
            "<b>Proportion :</b> %{y} %<extra></extra>"
    )
    )
    # Création des frames pour l'animation
    frames = []
    for annee in annees_age :
        df_pvd = city_data_pop_age[city_data_pop_age["Année"] == annee]
        df_terr = terr_data_pop_age[terr_data_pop_age["Année"] == annee]

        ages = df_pvd["Tranche_age"].unique()
    
        tot_pvd = sum(df_pvd["Effectif"])
        tot_terr = sum(df_terr["Effectif"])

        ages_pvd_prop = [round((x / tot_pvd), 4) * 100 for x in df_pvd["Effectif"]]
        ages_terr_prop = [round((x / tot_terr), 4) * 100 for x in df_terr["Effectif"]]

        frames.append(pgo.Frame(
            data = [
                pgo.Bar(x = ages, y = ages_pvd_prop),
                pgo.Bar(x = ages, y = ages_terr_prop)
            ],
         name = str(annee)
        ))

    fig323.update(frames = frames)

    # Ajout du slider et des boutons de lecture
    fig323.update_layout(
    sliders = [{
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {"font": {"size": 16}, 
                         "prefix": "Année :",
                         "visible": True,
                         "xanchor": "right"
                         },
        "transition": {"duration": 300, 
                       "easing": "cubic-in-out"
                       },
        "pad": {"b": 10, 
                "t": 10
                },
        "len": 0.9,
        "x": 0.1,
        "y": -0.1,
        "steps": [{"args": [[str(annee)], 
                            {"frame": {"duration": 300, "redraw": True}, 
                             "mode": "immediate"}
                            ],
                   "label": str(annee), 
                   "method": "animate"}
                  for annee in annees_age
                  ]
    }],
    title = f"Répartition de la population en fonction de <b>l'âge</b> <br>à {selected_city} {territoire_name}",
    xaxis_title = "Tranches d'âge",
    yaxis_title = f"Part de la population concernée <br>(en %)",
    barmode = 'group',
    template = 'plotly',
    plot_bgcolor = col_plot_background,
    height = 500
    )
    
    # Carte
    
    if territoire_selected == "Canton":
        carte = carte_comcom(selected_city)
    elif territoire_selected == "Département":
        carte = carte_departement(selected_city)
    else :
        carte = carte_region(selected_city)
    
    return html.Div([
        html.Div([
        html.Div([dcc.Graph(figure=fig321)], style={"width": "49%", "display": "inline-block"}),
        html.Div([dcc.Graph(figure=fig322)], style={"width": "49%", "display": "inline-block"})
        ], style={"display": "flex", "justify-content": "space-between", "margin-top": "10px"}
                 ),
        html.Div([
        html.Div([dcc.Graph(figure=fig323)], style={"width": "49%", "display": "inline-block"}),
        html.Div([dcc.Graph(figure=carte)], style={"width": "49%", "display": "inline-block"})
        ], style={"display": "flex", "justify-content": "space-between", "margin-top": "20px"})
        ])


# Fonction pour les graphes sur la répartition des classes socio-professionnelles
def graphiques_cs_pop(selected_city,territoire_selected):
    insee_selected = programme_pvd.loc[programme_pvd["lib_com"] == selected_city, "insee_com"].values[0]
    annee_selected = 2021
    
    territoire_name2 = ""
    if territoire_selected == "Canton":
        territoire_name2 = "dans le canton"
    else :
        territoire_name2 = "en " + recup_nom_territoire(selected_city,territoire_selected)
    
    # 1 Treemap petite ville
    city_data_cs_sexe = data_cs_selon_sexe[(data_cs_selon_sexe["insee_com"] == insee_selected) & (data_cs_selon_sexe["Année"] == annee_selected)]
    city_data_cs_sexe = city_data_cs_sexe.sort_values(by = ["Classe", "Sexe"])

    # Listes des classes
    effectif_classes = city_data_cs_sexe.groupby("Classe")["Effectif"].sum().reset_index()

    # labels, parents et values
    labels = list(effectif_classes["Classe"]) + list(city_data_cs_sexe["Sexe"])
    parents = ["Population"] * len(effectif_classes) + list(city_data_cs_sexe["Classe"])
    values = list(effectif_classes["Effectif"]) + list(city_data_cs_sexe["Effectif"])

    labels.insert(0, "Population")
    parents.insert(0, "")
    values.insert(0, city_data_cs_sexe["Effectif"].sum())
    
    df = pd.DataFrame(
    {"labels" : labels,
     "parents" : parents,
     "values" : values
    }    
    )

    # Création d'un dictionnaire des valeurs parentales
    parent_values = {label: value for label, value in zip(df["labels"], df["values"])}

    # Calcul de la part
    df["part"] = df.apply(lambda row: round(row["values"] / parent_values[row["parents"]], 3) * 100
                      if row["parents"] in parent_values and parent_values[row["parents"]] != 0 else 100, axis=1)


    # Générer la liste des couleurs dans l'ordre des labels
    colors = [color_dict[label] for label in labels]
    
    # Création du treemap
    fig331 = pgo.Figure(pgo.Treemap(
    labels = labels,
    parents = parents,
    values = values,
    maxdepth = 2, # affiche aucune case sexe sauf si la cs est cliquée
    marker = dict(colors = colors),
    name = "",
    customdata = df,
    hovertemplate = "<b>Classe :</b> %{customdata[0]} <br>"
                    "<b>Effectif :</b> %{customdata[2]} <br>"
                    "<b>Proportion :</b> %{customdata[3]} %<extra></extra>"
    ))

    fig331.update_traces(tiling = dict(packing = "squarify"))

    fig331.update_layout(
    # margin = dict(t = 50, l = 5, r = 5, b = 5),
    title = f"Répartition de la population selon <b>la classe sociale et le sexe</b> <br>à {selected_city} en {annee_selected}",
    )
    
    # 2 Treemap du territoire sélectionné
    if territoire_selected == "Canton" :
        comcom_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Communauté de commune"].values[0]
        dep_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Département"].values[0]
        
        comcom_data_cs_sexe = data_cs_selon_sexe[data_cs_selon_sexe["Communauté de commune"] == comcom_selected]
        comcom_data_cs_sexe = comcom_data_cs_sexe[comcom_data_cs_sexe["Département"] == dep_selected]
        comcom_data_cs_sexe = comcom_data_cs_sexe[comcom_data_cs_sexe["Année"] == annee_selected]
        comcom_data_cs_sexe = comcom_data_cs_sexe.groupby(["Année", "Communauté de commune", "Classe", "Sexe"], as_index = False)[["Effectif"]].sum()

        terr_data_cs_sexe = comcom_data_cs_sexe
    elif territoire_selected == "Département" :
        dep_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Département"].values[0]
        
        dep_data_cs_sexe = data_cs_selon_sexe[data_cs_selon_sexe["Département"] == dep_selected]
        dep_data_cs_sexe = dep_data_cs_sexe[dep_data_cs_sexe["Année"] == annee_selected]
        dep_data_cs_sexe = dep_data_cs_sexe.groupby(["Année", "Département", "Classe", "Sexe"], as_index = False)[["Effectif"]].sum()
        
        terr_data_cs_sexe = dep_data_cs_sexe
    else :
        reg_selected = donnees_communes[donnees_communes["insee_com"] == insee_selected]["Région"].values[0]
        reg_data_cs_sexe = data_cs_selon_sexe[data_cs_selon_sexe["Région"] == reg_selected]
        reg_data_cs_sexe = reg_data_cs_sexe[reg_data_cs_sexe["Année"] == annee_selected]
        reg_data_cs_sexe = reg_data_cs_sexe.groupby(["Année", "Région", "Classe", "Sexe"], as_index = False)[["Effectif"]].sum()

        terr_data_cs_sexe = reg_data_cs_sexe

    terr_data_cs_sexe = terr_data_cs_sexe.sort_values(by = ["Classe", "Sexe"])

    # Listes des effectifs par classes
    effectif_classes = terr_data_cs_sexe.groupby("Classe")["Effectif"].sum().reset_index()

    # labels, parents et values
    labels = list(effectif_classes["Classe"]) + list(terr_data_cs_sexe["Sexe"])
    parents = ["Population"] * len(effectif_classes) + list(terr_data_cs_sexe["Classe"])
    values = list(effectif_classes["Effectif"]) + list(terr_data_cs_sexe["Effectif"])

    labels.insert(0, "Population")
    parents.insert(0, "")
    values.insert(0, terr_data_cs_sexe["Effectif"].sum())
    
    df = pd.DataFrame(
    {"labels" : labels,
     "parents" : parents,
     "values" : values
    }    
    )

    # Création d'un dictionnaire des valeurs parentales
    parent_values = {label: value for label, value in zip(df["labels"], df["values"])}

    # Calcul de la part
    df["part"] = df.apply(lambda row: round(row["values"] / parent_values[row["parents"]], 3) * 100
                      if row["parents"] in parent_values and parent_values[row["parents"]] != 0 else 100, axis=1)
    
    # Générer la liste des couleurs dans l'ordre des labels
    colors = [color_dict[label] for label in labels]

    # Création du treemap
    fig332 = pgo.Figure(pgo.Treemap(
    labels = labels,
    parents = parents,
    values = values,
    maxdepth = 2, # affiche aucune case sexe sauf si la cs est cliquée
    marker = dict(colors = colors),
        name = "",
    customdata = df,
    hovertemplate = "<b>Classe :</b> %{customdata[0]} <br>"
                    "<b>Effectif :</b> %{customdata[2]} <br>"
                    "<b>Proportion :</b> %{customdata[3]} %<extra></extra>"
    ))

    fig332.update_traces(tiling = dict(packing = "squarify"))

    fig332.update_layout(
    # margin = dict(t = 50, l = 5, r = 5, b = 5),
    title = f"Répartition de la population selon <b>la classe sociale et le sexe </b><br>{territoire_name2} en {annee_selected}",
    )

    if territoire_selected == "Canton":
        carte = carte_comcom(selected_city)
    elif territoire_selected == "Département":
        carte = carte_departement(selected_city)
    else :
        carte = carte_region(selected_city)

    return html.Div([
        html.Div([
        html.Div([dcc.Graph(figure=fig331)], style={"width": "49%", "display": "inline-block"}),
        html.Div([dcc.Graph(figure=fig332)], style={"width": "49%", "display": "inline-block"})
        ], style={"display": "flex", "justify-content": "space-between", "margin-top": "10px"}
                 ),
        html.Div([
        html.Div([dcc.Graph(figure=carte)])
        ], style={"display": "flex", "justify-content": "space-between", "margin-top": "20px"})
        ])


# # 4 Regroupement des pages et callback

# Définition du layout de l'application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    # Nav bar
    html.Div([
        dcc.Link('Accueil', href='/',style={'color':col_navbar_text}),
        dcc.Link('Ma petite ville', href='/ma-petite-ville', style={'marginLeft': '20px','color':col_navbar_text}),
        dcc.Link('Comparaison aux autres territoires', href='/comparaison-aux-autres-territoires', style={'marginLeft': '20px','color':col_navbar_text})
    ], style={'padding': '10px', 'backgroundColor': col_navbar,'font-family': 'Arial'}),

    html.Div(id='page-content')  # Conteneur dynamique
], 
style={'backgroundColor': col_background} # Couleur arrière plan
)



# Sélection de la page
@app.callback(dd.Output('page-content', 'children'),
              dd.Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/ma-petite-ville':
        return petite_ville_layout
    elif pathname == '/comparaison-aux-autres-territoires':
        return comparaison_layout
    else:
        return home_layout  # Page d'accueil par défaut



# Animation KPI du nombre de petites villes de demain
@app.callback(
    Output("kpi-display", "children"),
    Input("interval-component", "n_intervals")
)
def update_kpi(n):
    # Calcul de la valeur actuelle (animation linéaire)
    valeur_actuelle = min(nombres_petites_villes, int(nombres_petites_villes * (n / 100)))  
    return f"{valeur_actuelle}"  # Affichage du nombre


# Pour switcher entre cartes des départements et des régions
@app.callback(
    [Output("graph-switch", "figure"),
     Output("switch-button", "children")],  # Change aussi le texte du bouton
    Input("switch-button", "n_clicks")
)
def switch_figure(n_clicks):
    if n_clicks % 2 == 0:
        return carte_pvd_departements, "Carte par régions"  # Affiche la carte 2 et propose de voir la 3
    else:
        return carte_pvd_regions, "Carte par départements"  # Affiche la carte 3 et propose de voir la 2

# Bouton d'information
@app.callback(
    Output("modal-info", "is_open"),
    [Input("open-info", "n_clicks"), Input("close-info", "n_clicks")],
    [dash.dependencies.State("modal-info", "is_open")]
)
def toggle_modal(open_clicks, close_clicks, is_open):
    if open_clicks > close_clicks:
        return True  # Ouvre la pop-up
    return False  # Ferme la pop-up

# Affichage graphiques page 2

@app.callback(
    [Output('output-page-2', 'children'), 
     Output("naissance-deces-page-2", "figure"), 
     Output("evolution-population-page-2", "figure"), 
     Output("pyramide-page-2", "figure"),
     Output("treemap-cs-sexe-page-2", "figure")],
    [Input('dropdown-commune-page-2', 'value')]
)
def update_output(selected_city):
    if selected_city is None :
        return f"Veuillez sélectionner une commune.", px.scatter(), px.scatter(), px.scatter(), px.scatter()
    
    # Récupérer le code INSEE de la ville sélectionnée
    insee_selected = programme_pvd[programme_pvd["lib_com"] == selected_city]["insee_com"].values[0]

    # Filtrer les données
        #Naissance et décès
    city_data_naiss = naissances[naissances["insee_com"] == insee_selected]
    city_data_deces = deces[deces["insee_com"] == insee_selected]
        # Taille de la population
    city_data_pop = data_age_population_generale[(data_age_population_generale["insee_com"] == insee_selected) & (data_age_population_generale["Tranche_age"] == "Total")]
    city_data_pop = city_data_pop.sort_values(by = "Année")   # pour être sûr de l'ordre
    city_data_pop["Variation"] = round(city_data_pop["Effectif"].pct_change() * 100, 2) # Calcul de la variation
    city_data_pop.fillna(0, inplace = True)
        #Pyramide des âges
    city_data_sexe_age = data_age_selon_sexe[data_age_selon_sexe["insee_com"] == insee_selected]
        # Treemap classes sociales
    annee = 2021
    city_data_cs_sexe = data_cs_selon_sexe[(data_cs_selon_sexe["insee_com"] == insee_selected) & (data_cs_selon_sexe["Année"] == annee)]

    # Appel de fonction pour la création des figures.

    # FIGURE 1 : Barplot des effectifs de naissances et des décès
    barplot_naissance_deces = graphique_naissance_deces(city_data_naiss,city_data_deces,selected_city)
    
    # FIGURE 2 : Variation de la taille de la population
    linechart_taille_pop = graphique_linechart_taille_pop(city_data_pop,selected_city)
    
    # FIGURE 3 : Pyramide des âges
    pyramide = graphique_pyramide(city_data_sexe_age,selected_city)

    # FIGURE 4 : Treemap des classes socio-profesionnelles
    treemap = graphique_treemap(city_data_cs_sexe,selected_city)

    return  f"-----", barplot_naissance_deces, linechart_taille_pop, pyramide, treemap


# Affichage graphiques page 3
@app.callback(
    Output('output-page-3', 'children'),
    [Input('dropdown-commune-page-3', 'value'),
     Input('dropdown-territoire-page-3', 'value'),
     Input('dropdown-critere-page-3', 'value')]  # Ajout d'un critère sélectionné
)
def update_output(selected_city, territoire_selected, critere_selected):
    if selected_city is None:
        return f"Veuillez sélectionner une commune."
    if territoire_selected is None:
        return f"Veuillez sélectionner un territoire."
    if critere_selected is None:
        return f"Veuillez sélectionner un critère de comparaison."
    
    # Squelette pour les graphiques en fonction du critère sélectionné
    if critere_selected == "Evolution de la taille de la population":
        return graphiques_taille_pop(selected_city,territoire_selected)
    
    elif critere_selected == "Age de la population":
        return graphiques_age_pop(selected_city,territoire_selected)
    
    elif critere_selected == "Classes socio-professionnelles de la population":
        return graphiques_cs_pop(selected_city,territoire_selected)
    
    # Par défaut, si aucun critère sélectionné
    return f"Veuillez sélectionner un critère de comparaison."


# # 5 Dashboard

# Démarre Dash
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
#app.run_server(threaded=True, mode="external")

