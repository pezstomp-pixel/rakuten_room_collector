# collectors/item_search.py

import os
import time
from typing import List, Dict, Any

import requests

from config import (
    ICHIBA_ITEM_SEARCH_URL,
    RAKUTEN_APP_ID,
    RAKUTEN_ACCESS_KEY,
    REQUEST_TIMEOUT,
    DEFAULT_HITS,
    MAX_PAGES_PER_KEYWORD,
    MIN_AFFILIATE_RATE,
)

# Webアプリケーションタイプのキーで叩くときに必要になるヘッダー
# （バックエンドタイプで叩くときも悪さはしないので、常に付けてしまってOK）
HEADERS = {
    "Referer": "https://github.com/",
    "Origin": "https://github.com/",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}


def fetch_search_items(keyword: str) -> List[Dict[str, Any]]:
    """キーワードで楽天市場アイテム検索APIを叩き、Items配列をまとめて返す。"""
    all_items: List[Dict[str, Any]] = []

    for page in range(1, MAX_PAGES_PER_KEYWORD + 1):
        params = {
            "applicationId": RAKUTEN_APP_ID,
            "accessKey": RAKUTEN_ACCESS_KEY,
            "keyword": keyword,
            "hits": DEFAULT_HITS,
            "page": page,
            "format": "json",
            "formatVersion": 2,
            # フィルタ
            "minAffiliateRate": MIN_AFFILIATE_RATE,
            "hasReviewFlag": 1,
            # 並び順
            "sort": "-reviewCount",
        }

        try:
            resp = requests.get(
                ICHIBA_ITEM_SEARCH_URL,
                params=params,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as e:
            print(
                f"[ERROR] request failed: keyword={keyword}, "
                f"page={page}, error={e}"
            )
            break

        if resp.status_code != 200:
            print(f"[WARN] status={resp.status_code} keyword={keyword} page={page}")
            print(resp.text[:300])
            break

        data = resp.json()
        items = data.get("Items", [])

        if not items:
            print(f"[INFO] no items: keyword={keyword}, page={page}")
            break

        all_items.extend(items)

        page_count = int(data.get("pageCount", 0) or 0)
        last = int(data.get("last", 0) or 0)

        if page_count and page >= page_count:
            break
        if last and page >= last:
            break

        time.sleep(1.1)

    return all_items