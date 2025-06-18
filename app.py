import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta

st.set_page_config(page_title="Euribor 3M – Quotidien (scraping)", layout="centered")
st.title("Euribor 3 mois (quotations journalières)")

# Nombre de jours à afficher (entre 1 et 365)
n = st.number_input("Nombre de derniers jours", min_value=1, max_value=365, value=30)

@st.cache_data(ttl=3600)
def fetch_euribor_3m_daily_scrape(last_n: int) -> pd.DataFrame:
    """
    Scraping de la table 'By day' sur euribor-rates.eu pour récupérer
    les last_n dernières cotations journalières du 3M Euribor.
    """
    url = "https://www.euribor-rates.eu/en/current-euribor-rates/2/euribor-rate-3-months/"
    resp = requests.get(url)
    resp.raise_for_status()

    # Parser le HTML et trouver la section <h2>By day</h2> puis le tableau qui suit
    soup = BeautifulSoup(resp.text, "html.parser")
    heading = soup.find("h2", string="By day")
    if not heading:
        raise ValueError("Impossible de trouver la section 'By day' sur la page.")
    table = heading.find_next("table")
    if not table:
        raise ValueError("Tableau introuvable après le titre 'By day'.")

    # Lire le tableau en DataFrame
    df = pd.read_html(str(table))[0]
    # Normaliser les colonnes et le type date
    df.columns = ["Date", "Euribor 3M (%)"]
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=False)  # format mm/dd/YYYY
    df = df.set_index("Date").sort_index(ascending=False)

    # Ne garder que les last_n premiers
    return df.head(last_n)

# Exécution et affichage
try:
    df = fetch_euribor_3m_daily_scrape(n)
    if df.empty:
        st.warning("Aucune donnée disponible.")
    else:
        st.line_chart(df["Euribor 3M (%)"])
        st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lors de la récupération : {e}")
