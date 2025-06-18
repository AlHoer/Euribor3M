import requests
import pandas as pd
from io import StringIO
from datetime import date, timedelta

def fetch_euribor_3m_bundesbank(start: str, end: str) -> pd.DataFrame:
    """
    Récupère le taux Euribor 3M (quotations journalières) depuis la Bundesbank.
    start, end au format 'YYYY-MM-DD'.
    """
    flow_ref = "BBIG1"
    series_key = "D.D0.EUR.MMKT.EURIBOR.M03.BID._Z"
    url = f"https://api.statistiken.bundesbank.de/rest/data/{flow_ref}/{series_key}"
    params = {
        "startPeriod": start,  # ex. '2025-05-18'
        "endPeriod": end,      # ex. '2025-06-17'
        "format": "csv"        # renvoie du SDMX-CSV prêt pour pandas.read_csv
    }
    resp = requests.get(url, params=params)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("Erreur HTTP :", resp.status_code, resp.text)
        raise

    # Chargement et nettoyage
    df = pd.read_csv(StringIO(resp.text))
    df = df.rename(columns={
        "TIME_PERIOD": "Date",
        "OBS_VALUE": "Euribor 3M (%)"
    })
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date")

if __name__ == "__main__":
    # Exemple : les 30 derniers jours
    today = date.today()
    start = (today - timedelta(days=30)).isoformat()
    end = today.isoformat()

    df = fetch_euribor_3m_bundesbank(start, end)
    print(df)

