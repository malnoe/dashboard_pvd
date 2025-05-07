import os
import gdown

# Liste des fichiers à télécharger : {nom_local: ID Google Drive}
fichiers = {
    "data_dashboard/data_cs_selon_sexe.csv": "1SJS2vBHbctlav4nJIWjb-_Rzn9JTiapz",
    "data_dashboard/data_age_selon_sexe.csv": "1kS-P8P_IyGsZh2MWJpaT_QU-CZ6aTaU8",
    "data_dashboard/data_age_population_generale.csv": "15Uj6m1aJ08MJusuRWne8KLnaQ5e3Yogi",
    "data_dashboard/contours_communes.json": "1_iN3XHQWx6CC4l04qc4CDq6ITK4o3BXL",
}

# Crée le dossier s’il n'existe pas
os.makedirs("data_dashboard", exist_ok=True)

for fichier_local, id_drive in fichiers.items():
    if not os.path.exists(fichier_local):
        url = f"https://drive.google.com/uc?id={id_drive}"
        print(f"Téléchargement de {fichier_local}...")
        gdown.download(url, fichier_local, quiet=False)
    else:
        print(f"{fichier_local} déjà présent.")
