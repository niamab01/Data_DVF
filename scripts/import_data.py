import sys
import sqlite3
import pandas as pd

print("Connexion à la base de données...")
conn = sqlite3.connect('dvf_database.db')

print("Lecture du fichier DVF (cela peut prendre un peu de temps)...")
# 🚨 ATTENTION : Ajuste le nom du fichier s'il s'appelle différemment (ex: '54.csv' ou 'valeursfoncieres-2025.txt')
# Le séparateur pour les fichiers officiels DVF est souvent la barre verticale '|' ou le point-virgule ';'
nom_fichier = sys.argv[1]
df = pd.read_csv(nom_fichier, sep='|', low_memory=False)

# Pour l'instant, on garde les colonnes qui correspondent exactement à ta table SQL
# Regarde les vrais noms des colonnes dans ton fichier texte et adapte-les ici !
colonnes_utiles = [
    'Valeur fonciere',
    'Date mutation', 
    'Code departement', 
    'Type local', 
    'Surface reelle bati',
    'Commune',
    'Code postal'
]

df_selection = df[colonnes_utiles].copy()

# Renomme les colonnes pour qu'elles collent EXACTEMENT aux noms de ta table SQL
df_selection.columns = [
    'valeur_fonciere', 
    'date_mutation', 
    'code_departement', 
    'type_local', 
    'surface_reelle_bati',
    'commune',
    'code_postal'
]
df_selection['valeur_fonciere'] = df_selection['valeur_fonciere'].astype(str)

# 2. On supprime les espaces cachés et on remplace la virgule par un point
df_selection['valeur_fonciere'] = df_selection['valeur_fonciere'].str.replace(' ', '', regex=False)
df_selection['valeur_fonciere'] = df_selection['valeur_fonciere'].str.replace(',', '.', regex=False)

# 3. On convertit enfin en vrai nombre décimal
df_selection['valeur_fonciere'] = pd.to_numeric(df_selection['valeur_fonciere'], errors='coerce')
print("Insertion des données dans SQLite...")
# if_exists='append' permet d'ajouter les lignes sans écraser la table
df_selection.to_sql('mutations', con=conn, if_exists='append', index=False)

conn.close()
print("Importation réussie !")