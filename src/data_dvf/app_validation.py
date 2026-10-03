import streamlit as st
import joblib
import pandas as pd

def charger_modele(type_local):
    nom_fichier = f"modele_{type_local.replace(' ', '_').replace('.', '')}.pkl"
    model = joblib.load(nom_fichier)
    return model

def verifier_transaction(type_local, valeur_fonciere, surface_reelle_bati):
    prix_m2 = valeur_fonciere / surface_reelle_bati
    model = charger_modele(type_local)
    
    X_nouvelle = pd.DataFrame({
        'prix_m2': [prix_m2],
        'surface_reelle_bati': [surface_reelle_bati]
    })
    
    resultat = model.predict(X_nouvelle)
    return resultat[0], prix_m2

st.title("🏠 Validation de transaction immobilière")

type_local = st.selectbox("Type de bien", ['Maison', 'Appartement', 'Local industriel. commercial ou assimilé'])
valeur_fonciere = st.number_input("Valeur foncière (€)", min_value=0.0)
surface_reelle_bati = st.number_input("Surface (m²)", min_value=1.0)

if st.button("Vérifier la transaction"):
    res, prix_m2 = verifier_transaction(type_local,valeur_fonciere,surface_reelle_bati)
    if res==-1:
        st.error(f"Anomalie détectée — prix au m² : {prix_m2:.2f}€/m². Confirmation manuelle requise.")
    else:
        st.success(f"Transaction normale — prix au m² : {prix_m2:.2f}€/m²")
    
