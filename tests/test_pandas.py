import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# On crée un faux tableau d'immobilier avec des bugs
data = {
    'ville': ['Nancy', 'Metz', 'Nancy', 'Thionville', 'Nancy', 'Metz'],
    'prix': ['300 000', '250,000', 'Inconnu', '180000', '15000000', None],
    'surface': [80, 70, 120, 0, 10, 85],
    'date': ['2026-01-05', '2026-02-12', '2026-01-20', '2026-03-01', '2026-02-15', '2026-01-18']
}

df = pd.DataFrame(data)
print("--- Données Brutes ---")
print(df)



df['prix'] = df['prix'].str.replace(' ', '')
df['prix'] = df['prix'].str.replace(',', '')
df['prix'] = pd.to_numeric(df['prix'], errors='coerce')

valeur_mediane = df['prix'].median()
df['prix'] = df['prix'].fillna(valeur_mediane)

df = df[(df['surface']>0) & (df['prix']>0)]

df['date'] = pd.to_datetime(df['date'])

df['mois'] = df['date'].dt.month
prix_moyen_par_ville = df.groupby('ville')['prix'].mean()
print(prix_moyen_par_ville)

df.to_csv('DVF.csv')

'''SELECT 
    SUBSTR(date_mutation, 4, 2) AS mois,
    COUNT(*) AS nombre_ventes,
    ROUND(SUM(valeur_fonciere), 2) AS volume_financier_total
FROM mutations
WHERE valeur_fonciere > 0
GROUP BY mois
ORDER BY mois ASC;'''

prix_moyen_par_ville.plot(kind='bar', color=['#4C72B0', '#C44E52'])

plt.title("Prix moyen des biens par ville")
plt.xlabel("Villes")
plt.ylabel("Prix moyen (€)")
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.savefig('graphique_villes.png', dpi=300, bbox_inches='tight')
print("Graphique généré avec succès dans ton dossier !")