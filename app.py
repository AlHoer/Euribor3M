import streamlit as st
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def fetch_html(url: str) -> str:
    """Retrieve fully rendered HTML from a URL using headless Chrome."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        html = driver.page_source
    finally:
        driver.quit()
    return html


st.title("WebScrapping App")

url = st.text_input("Entrez l'URL à scraper:")

if url:
    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else "Pas de titre"
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
