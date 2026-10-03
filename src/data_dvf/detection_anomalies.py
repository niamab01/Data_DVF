import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt

conn = sqlite3.connect('dvf_database.db')

#query = """
#SELECT 
#    code_postal,
#    type_local,
#    valeur_fonciere,
#    surface_reelle_bati, 
#    valeur_fonciere/surface_reelle_bati AS prix_m2
#FROM mutations
#WHERE valeur_fonciere>0 AND surface_reelle_bati BETWEEN 5 AND 2000
#"""
#df = pd.read_sql_query(query, conn)

#print(f"Nombre de transactions chargées : {len(df)}")
#print(df.head())
#print(df.describe())

### afficher les 10 transactions avec le prix_m2 le plus élevé et regarder leurs surface_reelle_bati et valeur_fonciere individuellemen

#query_top10 = """
#SELECT surface_reelle_bati, valeur_fonciere, valeur_fonciere/surface_reelle_bati AS prix_m2
#FROM mutations
#ORDER BY prix_m2 DESC
#LIMIT 10
#"""
#df_top10 = pd.read_sql_query(query_top10, conn)

#print(df_top10)

#query_verif = """
#SELECT date_mutation, code_postal, surface_reelle_bati, valeur_fonciere
#FROM mutations
#WHERE valeur_fonciere = 695000000
#"""
#df_verif = pd.read_sql_query(query_verif, conn)
#print(df_verif)

#query_clean = """
#SELECT valeur_fonciere, date_mutation, COUNT(*) AS nb_lots
#FROM mutations
#GROUP BY valeur_fonciere, date_mutation
#HAVING COUNT(*)>1
#ORDER BY nb_lots DESC
#"""
#df_clean = pd.read_sql_query(query_clean, conn)
#print(df_clean)

#query_clean1 = """
#SELECT code_postal, type_local, surface_reelle_bati
#FROM mutations
#WHERE valeur_fonciere = 243596.0 AND date_mutation = '26/06/2025'
#LIMIT 20
#"""
#df_clean1 = pd.read_sql_query(query_clean1, conn)
#conn.close()
#print(df_clean1)

#Limite de SQLITE(NOT IN) : trop de lignes ==> pandas

query = """
SELECT 
    code_postal,
    type_local,
    valeur_fonciere,
    date_mutation,
    surface_reelle_bati, 
    valeur_fonciere/surface_reelle_bati AS prix_m2
FROM mutations
WHERE valeur_fonciere > 0 
  AND surface_reelle_bati BETWEEN 5 AND 2000
"""
df = pd.read_sql_query(query, conn)
conn.close()

print(f"Avant filtrage multi-lots : {len(df)} lignes")

# Identifie les groupes multi-lots
compte = df.groupby(['valeur_fonciere', 'date_mutation','code_postal']).size()
groupes_multilots = compte[compte > 1].index

# Exclut ces lignes
df['cle'] = list(zip(df['valeur_fonciere'], df['date_mutation'], df['code_postal']))
df = df[~df['cle'].isin(groupes_multilots)]
df = df.drop(columns=['cle'])

print(f"Après filtrage multi-lots : {len(df)} lignes")
print(df.describe())
print(df.nsmallest(10, 'valeur_fonciere'))

from sklearn.ensemble import IsolationForest
import joblib

res=[]
features = ['prix_m2', 'surface_reelle_bati']
X = df[features]

for type_bien in df['type_local'].unique():
    ss_df = df[df['type_local'] == type_bien]
    features = ['prix_m2', 'surface_reelle_bati']
    X = ss_df[features]
    model = IsolationForest(contamination=0.02, random_state=1)
    ss_df['anomalie'] = model.fit_predict(X)

    # NOUVELLE LIGNE : sauvegarde le modèle de cette catégorie
    nom_fichier = f"modele_{type_bien.replace(' ', '_').replace('.', '')}.pkl"
    joblib.dump(model, nom_fichier)
    print(f"Modèle sauvegardé : {nom_fichier}")

    nb_anomalies = (ss_df['anomalie'] == -1).sum()
    print(f"Anomalies détectées : {nb_anomalies}/ {len(ss_df)}, {type_bien}")

    res.append(ss_df)

df_final = pd.concat(res)

for type_bien in df_final['type_local'].unique():
    print(f"\n=== {type_bien} ===")
    sous_anomalies = df_final[(df_final['type_local'] == type_bien) & 
                                (df_final['anomalie'] == -1)].sort_values('prix_m2')
    print(sous_anomalies.head(5))
    print(sous_anomalies.tail(5))

verif = df_final[(df_final['valeur_fonciere'] == 40670610.95)]
print(verif)