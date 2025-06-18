import streamlit as st
import pandas as pd
import requests
import re
from io import StringIO
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Euribor 3M — 5 ans Journaliers", layout="wide")
st.title("Historique journalier du taux Euribor 3 mois (5 ans)")

@st.cache_data(ttl=3600)
def fetch_euribor_3m_5y():
    """
    Récupère les cotations journalières du 3M Euribor sur 5 ans
    en reculant la date de fin jusqu'à trouver des données.
    """
    # 1. Définir la période de début
    today = date.today()
    start = (today - relativedelta(years=5)).isoformat()

    flow_ref   = "BBIG1"
    series_key = "D.D0.EUR.MMKT.EURIBOR.M03.BID._Z"
    base_url   = f"https://api.statistiken.bundesbank.de/rest/data/{flow_ref}/{series_key}"

    # 2. Tenter plusieurs dates de fin (jusqu'à 7 jours en arrière)
    resp = None
    for offset in range(1, 8):
        end_candidate = (today - timedelta(days=offset)).isoformat()
        params = {
            "startPeriod": start,
            "endPeriod":   end_candidate,
            "format":      "csv"
        }
        r = requests.get(base_url, params=params)
        r.raise_for_status()
        if "TIME_PERIOD" in r.text:
            resp = r
            break

    if resp is None:
        raise RuntimeError("Aucune donnée trouvée sur les 7 derniers jours pour définir la date de fin.")

    # 3. Nettoyer le préambule SDMX-CSV
    lines = resp.text.splitlines()
    header_idx = next(i for i, L in enumerate(lines) if "TIME_PERIOD" in L)
    data = "\n".join(lines[header_idx:])

    # 4. Détecter le séparateur et charger dans pandas
    sep = "," if data.count(",") > data.count(";") else ";"
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

