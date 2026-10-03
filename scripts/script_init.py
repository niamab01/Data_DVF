import sqlite3

# 1. Connexion (crée le fichier dvf_database.db s'il n'existe pas)
conn = sqlite3.connect('dvf_database.db')

# 2. Création d'un curseur (l'outil qui exécute les commandes SQL)
cursor = conn.cursor()

# 3. Écriture de la requête SQL de création de table
# À toi de compléter les types (TEXT, REAL, INTEGER) selon la doc DVF !
script_sql = """
CREATE TABLE IF NOT EXISTS mutations (
    id_mutation INTEGER PRIMARY KEY AUTOINCREMENT,
    valeur_fonciere REAL,
    date_mutation TEXT,
    code_departement TEXT,
    type_local TEXT,
    surface_reelle_bati REAL,
    commune TEXT,
    code_postal TEXT,
);
"""

# 4. Exécution du script
cursor.execute(script_sql)

# 5. Validation et fermeture
conn.commit()
conn.close()

print("Base de données et table créées avec succès !")