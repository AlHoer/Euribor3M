import streamlit as st
import pandas as pd
import requests
import re
from io import StringIO
from datetime import date

st.set_page_config(page_title="Euribor 3M — Quotidien", layout="centered")
st.title("Euribor 3 mois (quotations journalières)")

# Nombre d'observations à récupérer
n = st.number_input("Nombre de jours", min_value=1, max_value=365, value=30)

@st.cache_data(ttl=3600)
def fetch_euribor_3m_daily(last_n: int) -> pd.DataFrame:
    """
    Récupère les last_n dernières cotations journalières du 3M Euribor
    via l'API SDMX Bundesbank.
    """
    flow_ref   = "BBIG1"
    series_key = "D.D0.EUR.MMKT.EURIBOR.M03.BID._Z"
    url = (
        f"https://api.statistiken.bundesbank.de/rest/data/"
        f"{flow_ref}/{series_key}"
        f"?lastNObservations={last_n}&format=csv"
    )
    resp = requests.get(url)
    resp.raise_for_status()

    # Couper le préambule SDMX-CSV avant la ligne d'en-tête
    lines = resp.text.splitlines()
    header_idx = next(
        (i for i, L in enumerate(lines) if L.startswith("TIME_PERIOD")),
        None
    )
    if header_idx is None:
        raise ValueError("Entête SDMX introuvable dans la réponse Bundesbank.")
    sep = ";" if ";" in lines[header_idx] else ","
    data = "\n".join(lines[header_idx:])

    # Chargement dans pandas
    df = pd.read_csv(StringIO(data), sep=sep)
    df = df.rename(columns={
        "TIME_PERIOD": "Date",
        "OBS_VALUE":    "Euribor 3M (%)"
    })
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).set_index("Date")
    return df.sort_index()

# Exécution et affichage
try:
    df = fetch_euribor_3m_daily(n)
    if df.empty:
        st.warning("Aucune donnée renvoyée.")
    else:
        st.line_chart(df["Euribor 3M (%)"])
        st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lors de la récupération des données : {e}")






