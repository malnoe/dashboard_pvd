import os
import gdown

# Liste des fichiers à télécharger : {nom_local: ID Google Drive}
fichiers = {
    "data_dashboard/data_cs_selon_sexe.csv": "1I2J3K4L5M6N7O8P9",
    "data_dashboard/data_age_selon_sexe.csv": "1A2B3C4D5E6F7G8H9",
    "data_dashboard/data_age_population_generale.csv": "1X2Y3Z4W5V6U7T8S9",
    "data_dashboard/contours_communes.json": "1Q2R3S4T5U6V7W8X9",
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
