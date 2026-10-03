import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('dvf_database.db')

query = """
SELECT code_departement, 
       ROUND(AVG(valeur_fonciere / surface_reelle_bati), 2) AS prix_m2
FROM mutations 
WHERE valeur_fonciere > 0 AND surface_reelle_bati > 0
GROUP BY code_departement
ORDER BY prix_m2 DESC
LIMIT 10;
"""
print("Extraction des données depuis la base SQL")
df_top10 = pd.read_sql_query(query, conn)

conn.close()
print("Génération du graphique")

plt.figure(figsize=(10, 6)) # On donne une taille agréable au graphique
colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5']

plt.bar(df_top10['code_departement'], df_top10['prix_m2'], color=colors, edgecolor='black', alpha=0.8)
plt.title("Top 10 des départements français les plus chers (Prix moyen au m²)", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Numéro de Département", fontsize=12, labelpad=10)
plt.ylabel("Prix moyen au m² (€)", fontsize=12, labelpad=10)
plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.savefig('top10_departements_chers.png', dpi=300, bbox_inches='tight')
print("Le fichier 'top10_departements_chers.png' a été généré!")
