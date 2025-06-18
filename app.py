import requests
import pandas as pd
import re
from io import StringIO
from datetime import date, timedelta

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

    # Split en lignes et chercher l'en-tête
    lines = resp.text.splitlines()
    header_idx = next(
        (i for i, line in enumerate(lines)
         if re.search(r'\bTIME_PERIOD\b', line)),
        None
    )
    if header_idx is None:
        raise ValueError(
            "Impossible de trouver la ligne d'en-tête dans la réponse de l'API Bundesbank. "
            "Contenu reçu :\n" + "\n".join(lines[:10])
        )

    # Déterminer le séparateur sur la ligne d'en-tête
    header_line = lines[header_idx]
    sep = ',' if ',' in header_line else ';'

    # Lire le CSV à partir de l'en-tête
    df = pd.read_csv(
        StringIO("\n".join(lines[header_idx :])),
        sep=sep
    )

    # Renommer et parser la date
    df = df.rename(columns={
        "TIME_PERIOD": "Date",
        "OBS_VALUE":    "Euribor 3M (%)"
    })
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])  # au cas où il y ait encore des lignes foireuses
    return df.set_index("Date")

if __name__ == "__main__":
    today = date.today()
    start = (today - timedelta(days=30)).isoformat()
    end   =  today.isoformat()

    try:
        df = fetch_euribor_3m_bundesbank(start, end)
        print(df)
    except Exception as e:
        print("Erreur lors de la récupération :", e)



