import streamlit as st
import pandas as pd
import requests
from datetime import date

st.set_page_config(page_title="Euribor 3M – 24 dernières obs.", layout="centered")
st.title("Euribor 3 mois (dernières 24 observations)")

@st.cache_data(ttl=3600)
def fetch_last_24():
    url = (
        "https://data-api.ecb.europa.eu/service/data/"
        "FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA"
        "?lastNObservations=24"
        "&detail=dataonly"
        "&format=jsondata"
    )
    resp = requests.get(url)
    resp.raise_for_status()
    js = resp.json()

    # 1) extraire la dimension des dates
    obs_dim = js["structure"]["dimensions"]["observation"][0]["values"]
    dates = [d["id"] for d in obs_dim]

    # 2) récupérer la série unique
    series = js["dataSets"][0]["series"]
    _, content = next(iter(series.items()))
    observations = content.get("observations", {})

    # 3) construire la liste de dicts
    records = []
    for idx_str, val in observations.items():
        idx = int(idx_str)
        records.append({
            "Date": dates[idx],
            "Euribor 3M (%)": val[0]
        })

    # 4) DataFrame final
    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date").sort_index()

# --- affichage ---
try:
    df = fetch_last_24()
    if df.empty:
        st.warning("Aucune observation renvoyée.")
    else:
        st.line_chart(df["Euribor 3M (%)"])
        st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lors de la récupération : {e}")






