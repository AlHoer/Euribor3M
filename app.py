import streamlit as st
import pandas_datareader.data as web
from datetime import date, timedelta

st.set_page_config(page_title="Euribor 3M via FRED", layout="centered")
st.title("Taux Euribor 3 mois (source FRED)")

# Sélecteurs de date
today = date.today()
start = st.date_input("Date de début", value=today - timedelta(days=30))
end   = st.date_input("Date de fin",   value=today)

@st.cache_data(ttl=3600)
def fetch_euribor_fred(start_date, end_date):
    return web.DataReader('IR3TIB01EZM156N', 'fred', start_date, end_date)

df = fetch_euribor_fred(start, end)
if df.empty:
    st.warning("Pas de données pour cette période.")
else:
    st.line_chart(df["IR3TIB01EZM156N"])
    st.dataframe(df)



