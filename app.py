import streamlit as st
import pandas as pd
import requests
import re
from io import StringIO
from datetime import date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Euribor 3M — 5 ans Journaliers", layout="wide")
st.title("Historique journalier du taux Euribor 3 mois (5 ans)")

@st.cache_data(ttl=3600)
def fetch_euribor_3m_5y() -> pd.DataFrame:
    """
    Récupère les cotations journalières du 3M Euribor sur 5 ans
    via l'API SDMX de la Bundesbank.
    """
    # 1. Définir la période : aujourd'hui et -5 ans
    today = date.today()
    start = (today - relativedelta(years=5)).isoformat()
    end   = today.isoformat()

    # 2. Construire l'URL et les params
    flow_ref   = "BBIG1"
    series_key = "D.D0.EUR.MMKT.EURIBOR.M03.BID._Z"
    url        = f"https://api.statistiken.bundesbank.de/rest/data/{flow_ref}/{series_key}"
    params = {
        "startPeriod": start,   # ex. '2020-06-18'
        "endPeriod":   end,     # ex. '2025-06-18'
        "format":      "csv"    # SDMX-CSV :contentReference[oaicite:0]{index=0}
    }

    # 3. Requête et vérif.
    resp = requests.get(url, params=params)
    resp.raise_for_status()

    # 4. Nettoyage SDMX-CSV : trouver la ligne d'en-tête contenant TIME_PERIOD
    lines = resp.text.splitlines()
    header_idx = next(
        (i for i, line in enumerate(lines) if "TIME_PERIOD" in line),
        None
    )
    if header_idx is None:
        raise ValueError("En-tête 'TIME_PERIOD' introuvable dans la réponse Bundesbank.")
    data = "\n".join(lines[header_idx:])

    # 5. Détection du séparateur
    sep = "," if data.count(",") > data.count(";") else ";"

    # 6. Lecture par pandas
    df = pd.read_csv(StringIO(data), sep=sep)
    df = df.rename(columns={
        "TIME_PERIOD": "Date",
        "OBS_VALUE":    "Euribor 3M (%)"
    })
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).set_index("Date").sort_index()

    return df

# Exécution et affichage
try:
    df = fetch_euribor_3m_5y()
    if df.empty:
        st.warning("Aucune donnée disponible pour cette période.")
    else:
        st.subheader("Courbe journalière sur 5 ans")
        st.line_chart(df["Euribor 3M (%)"])
        st.subheader("Tableau des valeurs")
        st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lors de la récupération : {e}")
