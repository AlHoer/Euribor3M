import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("WebScrapping App")

url = st.text_input("Entrez l'URL à scraper:")

if url:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'Pas de titre'
        st.header("Titre de la page")
        st.write(title)

        st.header("Paragraphe(s) trouvé(s)")
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        if paragraphs:
            for p in paragraphs[:5]:
                st.write(p)
        else:
            st.write("Aucun paragraphe trouvé.")
    except Exception as e:
        st.error(f"Erreur: {e}")
