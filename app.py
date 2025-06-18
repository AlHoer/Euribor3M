import streamlit as st
import pandas as pd
import requests
import re
from io import StringIO
from datetime import date, timedelta

st.set_page_config(page_title="Euribor 3M", layout="centered")
st.title("Taux Euribor 3 mois (quotations journalières)")

# Widgets de sélection de date
today = date.today()
end_date = st.date_input("Date de fin", value=today)
start_date = st.date_input("Date de début", value=today - timedelta(days=30))

@st.cache_data(ttl=3600)
def fetch_euribor_3m_bundesbank(start: str, end: str) -> pd.DataFrame:
    """
    Récupère le taux Euribor 3M (quotations journalières) depuis la Bundesbank.
    start, end au format 'YYYY-MM-DD'.
    """
    flow_ref   = "BBIG1"
    series_key = "D.D0.EUR.MMKT.EURIBOR.M03.BID._Z"
    url        = f"https://api.statistiken.bundesbank.de/rest/data/{flow_ref}/{series_key}"
    params = {
        "startPeriod": start,
        "endPeriod":   end,
        "format":      "csv"  # SDMX-CSV
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()

    # Split en lignes et chercher la ligne d'en-tête
    lines = resp.text.splitlines()
    header_idx = next(
        (i for i, line in enumerate(lines)
         if re.search(r'\bTIME_PERIOD\b', line)),
        None
    )
    if header_idx is None:
        raise ValueError("En-tête 'TIME_PERIOD' introuvable dans la réponse de l'API Bundesbank.")

    # Détecter le séparateur sur la ligne d'en-tête
    header_line = lines[header_idx]
    sep = ',' if ',' in header_line else ';'

    # Lire le CSV à partir de l'en-tête
    df = pd.read_csv(StringIO("\n".join(lines[header_idx:])), sep=sep)
    df = df.rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": "Euribor 3M (%)"})
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    return df.set_index("Date")

# Appel et affichage
try:
    df = fetch_euribor_3m_bundesbank(start_date.isoformat(), end_date.isoformat())
    if df.empty:
        st.warning("Aucune donnée disponible pour cette période.")
    else:
        st.line_chart(df["Euribor 3M (%)"])
        st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lors de la récupération des données : {e}")



