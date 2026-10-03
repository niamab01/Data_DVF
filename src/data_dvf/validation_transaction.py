import joblib
import pandas as pd

def charger_modele(type_local):
    """Charge le bon modèle selon le type de bien"""
    nom_fichier = f"modele_{type_local.replace(' ', '_').replace('.', '')}.pkl"
    model = joblib.load(nom_fichier)
    return model

def verifier_transaction(type_local, valeur_fonciere, surface_reelle_bati):
    # Calcul du prix au m²
    prix_m2 = valeur_fonciere / surface_reelle_bati
    
    # Chargement du bon modèle
    model = charger_modele(type_local)
    
    # Prépare les données dans le même format que l'entraînement
    X_nouvelle = pd.DataFrame({
        'prix_m2': [prix_m2],
        'surface_reelle_bati': [surface_reelle_bati]
    })
    
    # Prédiction
    resultat = model.predict(X_nouvelle)
    
    if resultat[0] == -1:
        print(f"ANOMALIE DÉTECTÉE — prix_m2 = {prix_m2:.2f}€/m²")
        print("Confirmation manuelle requise avant validation.")
    else:
        print(f"Transaction normale — prix_m2 = {prix_m2:.2f}€/m²")
    
    return resultat[0]

verifier_transaction('Maison', 200000, 80)
verifier_transaction('Maison', 1, 250)