# collectors/ranking.py
import requests
from config import ITEM_RANKING_ENDPOINT, RAKUTEN_APP_ID, REQUEST_TIMEOUT

def fetch_ranking_items(genre_id=None):
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "format": "json"
    }
    if genre_id:
        params["genreId"] = genre_id

    r = requests.get(ITEM_RANKING_ENDPOINT, params=params, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return data.get("Items", [])