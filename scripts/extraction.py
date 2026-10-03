import sqlite3
import pandas as pd

conn = sqlite3.connect('dvf_database.db')


# --- 1. EXTRACTION DEPT ---
print("⏳ Traitement des données par département...")
query_cp = """
SELECT 
    code_postal, 
    COUNT(*) AS nb_ventes, ROUND(AVG(valeur_fonciere/surface_reelle_bati),2) AS prix_m2, type_local 
FROM mutations
WHERE valeur_fonciere>0 AND surface_reelle_bati BETWEEN 10 AND 1000 AND type_local IN ('Maison', 'Appartement')
GROUP BY code_postal, type_local;
"""
df_dept = pd.read_sql_query(query_cp, conn)

query_median = """
SELECT 
    code_postal,
    type_local, (valeur_fonciere/surface_reelle_bati) AS prix_m2_raw
FROM mutations
WHERE valeur_fonciere>0 AND surface_reelle_bati BETWEEN 10 AND 1000 AND type_local IN ('Maison', 'Appartement');
"""
df_median_raw = pd.read_sql_query(query_median, conn)
df_median = (df_median_raw
             .groupby(['code_postal', 'type_local'])['prix_m2_raw']
             .median().round(2).reset_index().rename(columns={'prix_m2_raw': 'prix_m2_median'}))

df_dept = df_dept.merge(df_median, on=['code_postal', 'type_local'])

# --- LA LIGNE MAGIQUE : Traduction du code en vrai nom ---
df_dept['code_postal'] = (df_dept['code_postal']
                          .astype(str)
                          .str.replace('.0', '', regex=False)  # supprime le .0
                          .str.strip()
                          .str.zfill(5))
df_dept = df_dept.rename(columns={'code_postal': 'Code Postal'})
df_dept = df_dept.rename(columns={
    'nb_ventes': 'Nb Ventes',
    'prix_m2': 'Prix M2',
    'prix_m2_median': 'Prix M2 Median',
    'type_local': 'Type Local'
})
df_dept.to_csv('dvf_dept.csv', index=False)
print("✅ dvf_dept.csv généré avec les vrais noms !")


print("Traitement des tendances temporelles...")
query_tps = """
SELECT SUBSTR(date_mutation,7,4) AS annee,
       CASE
           WHEN SUBSTR(date_mutation,4,2) IN ('01', '02', '03') THEN 'T1'
           WHEN SUBSTR(date_mutation,4,2) IN ('04', '05', '06') THEN 'T2'
           WHEN SUBSTR(date_mutation,4,2) IN ('07', '08', '09') THEN 'T3'
           ELSE 'T4'
       END AS trimestre,
       type_local, 
       (valeur_fonciere / surface_reelle_bati) AS prix_m2_raw
FROM mutations 
WHERE valeur_fonciere > 0 AND surface_reelle_bati BETWEEN 10 AND 1000
  AND type_local IN ('Appartement', 'Maison');
"""
df_tps_raw = pd.read_sql_query(query_tps, conn)
df_tps = (df_tps_raw
          .groupby(['annee', 'trimestre', 'type_local'])['prix_m2_raw']
          .median()
          .round(2)
          .reset_index()
          .rename(columns={'prix_m2_raw': 'prix_m2_median'}))

df_tps['periode'] = df_tps['annee'].astype(str) + '-' + df_tps['trimestre']
df_tps = df_tps.sort_values(['annee', 'trimestre'])
df_tps.to_csv('dvf_temporel.csv', index=False)
print("dvf_temporel.csv généré")


query_distrib = """
SELECT type_local,
       (valeur_fonciere / surface_reelle_bati) AS prix_m2,
       surface_reelle_bati
FROM mutations
WHERE valeur_fonciere > 0
  AND surface_reelle_bati BETWEEN 10 AND 1000
  AND type_local IN ('Appartement', 'Maison')
  AND (valeur_fonciere / surface_reelle_bati) BETWEEN 500 AND 15000;
"""
df_distrib = pd.read_sql_query(query_distrib, conn)
df_distrib.to_csv('dvf_distribution.csv', index=False)
print("dvf_distribution.csv généré")

conn.close()
