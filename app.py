import requests
import pandas as pd
from io import StringIO
from datetime import date, timedelta

def fetch_euribor_3m_bundesbank(start: str, end: str) -> pd.DataFrame:
    """
    Récupère le taux Euribor 3M (quotations journalières) depuis la Bundesbank.
    start, end au format 'YYYY-MM-DD'.
    """
    series_id = 'BBIG1.D.D0.EUR.MMKT.EURIBOR.M03.BID._Z'
    url = f'https://api.statistiken.bundesbank.de/rest/data/{series_id}'
    params = {
        'startPeriod': start,
        'endPeriod': end,
        'format': 'csv'            # renvoie un CSV prêt à pd.read_csv
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    # On charge directement dans un DataFrame
    df = pd.read_csv(StringIO(resp.text))
    # Nettoyage minimal
    df = df.rename(columns={
        'TIME_PERIOD': 'Date',
        'OBS_VALUE': 'Euribor_3M (%)'
    })
    df['Date'] = pd.to_datetime(df['Date'])
    return df.set_index('Date')

# Ex. : les 30 derniers jours
today = date.today()
start = (today - timedelta(days=30)).isoformat()
end = today.isoformat()
df = fetch_euribor_3m_bundesbank(start, end)
print(df)

