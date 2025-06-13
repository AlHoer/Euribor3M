import socket
from urllib.parse import urlparse
import tempfile
import shutil
import re

import streamlit as st
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def fetch_page(url: str) -> tuple[str, list[str]]:
    """Retrieve rendered HTML and extract numbers using Playwright."""

    parsed = urlparse(url)
    if not (parsed.scheme and parsed.netloc):
        raise ValueError("URL invalide")

    try:
        socket.gethostbyname(parsed.hostname)
    except socket.gaierror as e:
        raise RuntimeError(f"Impossible de résoudre l'hôte {parsed.hostname}") from e

    profile = tempfile.mkdtemp()
    numbers = set()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile,
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=EnableRemoteDebugging",
            ],
        )
        page = context.new_page()

        def on_response(resp):
            if resp.request.resource_type == "fetch" and resp.status == 200:
                try:
                    text = resp.text()
                except Exception:
                    return
                for n in re.findall(r"\d+(?:[.,]\d+)?", text):
                    numbers.add(n.replace(",", "."))

        page.on("response", on_response)

        try:
            page.goto(url, timeout=300_000, wait_until="domcontentloaded")
            page.wait_for_timeout(5_000)
            body = page.evaluate("() => document.body.innerText || ''")
            for n in re.findall(r"\d+(?:[.,]\d+)?", body):
                numbers.add(n.replace(",", "."))
            html = page.content()
        except PlaywrightTimeoutError:
            raise RuntimeError("La page n'a pas chargé à temps.")
        finally:
            context.close()
            shutil.rmtree(profile, ignore_errors=True)

    return html, sorted(numbers, key=lambda x: float(x))


st.title("WebScrapping App")

url = st.text_input("Entrez l'URL à scraper:")

if url:
    try:
        html, numbers = fetch_page(url)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else "Pas de titre"
        st.header("Titre de la page")
        st.write(title)

        st.header("Paragraphe(s) trouvé(s)")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        if paragraphs:
            for p in paragraphs[:5]:
                st.write(p)
        else:
            st.write("Aucun paragraphe trouvé.")

        if numbers:
            st.header("Nombres détectés")
            st.write(", ".join(numbers))
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
