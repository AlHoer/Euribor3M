import requests
import pandas as pd
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
        "format":      "csv"   # renvoie du SDMX-CSV :contentReference[oaicite:0]{index=0}
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()

    # --- nettoyage SDMX-CSV ---
    lines = resp.text.splitlines()
    # trouver l'index de la ligne d'en-tête "TIME_PERIOD"
    header_idx = next(i for i, l in enumerate(lines) if l.startswith("TIME_PERIOD"))
    data_lines = lines[header_idx:]
    # détecter le séparateur (',' ou ';')
    sep = ";" if ";" in data_lines[0] else ","
    df = pd.read_csv(StringIO("\n".join(data_lines)), sep=sep)

    # renommage et formatage
    df = df.rename(columns={"TIME_PERIOD": "Date", "OBS_VALUE": "Euribor 3M (%)"})
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date")

if __name__ == "__main__":
    today = date.today()
    start = (today - timedelta(days=30)).isoformat()
    end   =  today.isoformat()

    df = fetch_euribor_3m_bundesbank(start, end)
    print(df)


