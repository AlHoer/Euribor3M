import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta

st.set_page_config(page_title="Euribor 3M", layout="centered")
st.title("Taux Euribor 3 mois (JSON via BCE)")

# 1. Sélection de la période
today = date.today()
end_date   = st.date_input("Date de fin",   value=today)
start_date = st.date_input("Date de début", value=today - timedelta(days=30))

@st.cache_data(ttl=3600)
def fetch_euribor_3m(start: str, end: str) -> pd.DataFrame:
    url = "https://data-api.ecb.europa.eu/service/data/FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA"
    params = {
        "startPeriod":  start,     # ex. '2025-05-19'
        "endPeriod":    end,       # ex. '2025-06-18'
        "detail":       "dataonly",
        "format":       "jsondata"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    js = resp.json()

    # 2. Extraction des dates (dimension 'observation')
    obs_dim = js["structure"]["dimensions"]["observation"][0]["values"]
    dates = [item["id"] for item in obs_dim]

    # 3. Récupération des observations (une seule série)
    series = js["dataSets"][0]["series"]
    _, content = next(iter(series.items()))
    obs = content["observations"]

    # 4. Construction du DataFrame
    records = []
    for idx, val in obs.items():
        records.append({
            "Date": dates[int(idx)],
            "Euribor 3M (%)": val[0]
        })
    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date").sort_index()

# 5. Affichage
try:
    df = fetch_euribor_3m(start_date.isoformat(), end_date.isoformat())
    if df.empty:
        st.warning("Aucune donnée disponible pour cette période.")
    else:
        st.line_chart(df["Euribor 3M (%)"])
        st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lors de la récupération : {e}")



