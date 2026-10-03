# Data DVF — French Real Estate Market Analysis
 
End-to-end data project built on DVF (Demandes de Valeurs Foncières), the French government's open dataset of every recorded property transaction. I worked with 5 years of data (2021–2025) and split the project into three parts: a Python cleaning pipeline feeding a SQLite database, Tableau dashboards for visual exploration, and an Isolation Forest module to flag suspicious prices.
 
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-E97627?logo=tableau&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
 
---
 
## Contents
 
- [Background](#background)
- [High-level flow](#high-level-flow)
- [Source data](#source-data)
- [ETL pipeline](#etl-pipeline)
- [Tableau dashboards](#tableau-dashboards)
- [Anomaly detection](#anomaly-detection)
- [Running the project](#running-the-project)
- [File tree](#file-tree)
---
 
## Background
 
France's tax authority (DGFiP) publishes every property sale on the mainland (minus Alsace-Moselle and Mayotte) as flat text files. The data is massive but messy — multi-lot transactions duplicate rows, date formats flip between French and ISO, and raw columns don't plug into BI tools without work.
 
I wanted to take these raw files all the way to something usable:
 
1. Build a Python pipeline that ingests, cleans, and loads everything into SQLite
2. Wire up Tableau dashboards to explore median prices and transaction volumes by department and quarter
3. Try unsupervised ML (Isolation Forest) to automatically spot outlier prices
---
 
## High-level flow
 
```
Raw files (.txt)            Python scripts             SQLite
ValeursFoncieres-20XX ──>  extraction.py  ──>  dvf_database
                           import_data.py              │
                                                       ▼
                                             Aggregated CSVs
                                                       │
                                         ┌─────────────┴──────────────┐
                                         │      Tableau Desktop       │
                                         │   maps, lines, bar charts  │
                                         └─────────────┬──────────────┘
                                                       │
                                                       ▼
                                             Isolation Forest
                                             (scikit-learn / joblib)
                                                       │
                                                       ▼
                                             Streamlit app
                                             (manual validation)
```
 
---
 
## Source data
 
| File | Year | Size |
|------|------|------|
| `ValeursFoncieres-2021.txt` | 2021 | ~613 MB |
| `ValeursFoncieres-2022.txt` | 2022 | ~614 MB |
| `ValeursFoncieres-2023.txt` | 2023 | ~498 MB |
| `ValeursFoncieres-2024.txt` | 2024 | ~456 MB |
| `ValeursFoncieres-2025.txt` | 2025 | ~485 MB |
 
Source: [data.gouv.fr — DVF](https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/)
 
These files are too heavy to version. Download them yourself and drop them at the project root before running anything.
 
---
 
## ETL pipeline
 
### Scripts
 
`extraction.py` reads the raw `.txt` files, parses columns, and handles the mixed date formats (French `dd/mm/yyyy` alongside ISO). `import_data.py` picks up from there and inserts the cleaned rows into the SQLite database `dvf_database`. `script_init.py` chains both in one go.
 
### What the cleaning actually does
 
DVF data has a few well-known headaches. A single sale can span multiple rows when several lots are involved — I grouped them with `groupby` so the same price isn't counted twice. Postal codes got zero-padded to 5 digits because Tableau handles them much better than department codes. Rows missing a real surface or with a sale price of zero or under €1,000 were dropped.
 
### Output CSVs
 
The pipeline writes out CSVs ready for Tableau:
 
| File | What's inside |
|------|---------------|
| `dvf_dashboard_departements.csv` | Aggregated metrics per department |
| `dvf_dashboard_temporel.csv` | Prices and volumes by quarter/year |
| `dvf_dept.csv` | Detailed per-department data |
| `dvf_distribution.csv` | Price distributions by property type |
| `dvf_temporel.csv` | Raw time series |
 
---
 
## Tableau dashboards
 
Three views built in Tableau from the exported CSVs.
 
### Median price map
 
A choropleth of mainland France, colored by each department's median price per m². The expensive hotspots (Paris region, the Riviera, Atlantic coast) stand out immediately.
 
 
### Quarterly trends
 
Median prices and transaction counts tracked quarter by quarter, with filters for property type (apartment, house, commercial).
 
### Price distribution and department ranking
 
Histograms of sale prices plus a ranking of the priciest departments.
 
Two static matplotlib charts (`graphique_villes.png` and `top10_departements_chers.png`) sit alongside these dashboards.
 
---
 
## Anomaly detection
 
### Why separate models
 
Apartments in central Paris and warehouses in rural Brittany live in completely different price universes, so training one global model would be pointless. I trained a dedicated Isolation Forest for each property category:
 
| `.pkl` file | Covers |
|-------------|--------|
| `modele_Appartement.pkl` | Apartments |
| `modele_Maison.pkl` | Houses |
| `modele_Local_industriel_commercial_ou_assimil.pkl` | Commercial / industrial premises |
 
### Input features
 
Sale price (`valeur_fonciere`), built surface (`surface_reelle_bati`), room count (`nombre_pieces_principales`), and a derived price-per-m².
 
### Scripts
 
`detection_anomalies.py` trains the models and serializes them with joblib. `validation_transaction.py` checks a single transaction against the right model. `app_validation.py` wraps it in a small Streamlit UI where you punch in a property's characteristics and see whether it gets flagged.
 
This part is a proof of concept — it shows that unsupervised ML can surface odd-looking deals in this dataset, not that it should replace a human review.
 
---
 
## Running the project
 
### Requirements
 
- Python 3.10+
- Tableau Desktop or Tableau Public (for the dashboards)
### Setup
 
```bash
git clone https://github.com/<your-username>/Data-DVF.git
cd Data-DVF
pip install -r requirements.txt
```
 
### Dependencies
 
```
pandas
scikit-learn
joblib
streamlit
matplotlib
```
 
(`sqlite3` ships with Python's standard library.)
 
### Usage
 
```bash
# grab the DVF files from data.gouv.fr, put them at the root
 
# run the full pipeline
python script_init.py
 
# launch the validation app
streamlit run app_validation.py
```
 
---
 
## File tree
 
```
Data-DVF/
│
├── README.md
├── requirements.txt
│
├── Scripts
│   ├── script_init.py               # runs the full pipeline
│   ├── extraction.py                # raw file parsing
│   ├── import_data.py               # SQLite loading
│   ├── graphique_dvf.py             # matplotlib charts
│   ├── detection_anomalies.py       # Isolation Forest training
│   ├── validation_transaction.py    # single-transaction check
│   ├── app_validation.py            # Streamlit UI
│   └── test_pandas.py               # exploration notebook
│
├── Database
│   └── dvf_database                 # SQLite, ~1 GB
│
├── CSV exports
│   ├── dvf_dashboard_departements.csv
│   ├── dvf_dashboard_temporel.csv
│   ├── dvf_dept.csv
│   ├── dvf_distribution.csv
│   └── dvf_temporel.csv
│
├── Models
│   ├── modele_Appartement.pkl
│   ├── modele_Maison.pkl
│   └── modele_Local_industriel_commercial_ou_assimil.pkl
│
├── Charts
│   ├── graphique_villes.png
│   └── top10_departements_chers.png
│
├── screenshots/                     # Tableau captures
│   ├── dashboard_carte.png
│   ├── dashboard_temporel.png
│   └── dashboard_distribution.png
│
└── (raw data — gitignored)
    ├── ValeursFoncieres-2021.txt
    ├── ValeursFoncieres-2022.txt
    ├── ValeursFoncieres-2023.txt
    ├── ValeursFoncieres-2024.txt
    └── ValeursFoncieres-2025.txt
```
 
---
 
## .gitignore
 
```gitignore
# raw data
ValeursFoncieres-*.txt
 
# database
dvf_database
 
# trained models
*.pkl
 
# heavy export
dvf_distribution.csv
 
# python
__pycache__/
*.pyc
.venv/
```
 
---
 
## Author
 
**Niama** — Data & AI engineering student, Télécom Nancy
 
---
 
## License
 
DVF data: [Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/) · Code: MIT](https://www.etalab.gouv.fr/licence-ouverte-open-licence/) · Code : MIT
 
