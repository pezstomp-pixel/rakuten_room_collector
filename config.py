from pathlib import Path
import os
from dotenv import load_dotenv

# .env 読み込み
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# 出力ディレクトリ
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 楽天APIの認証情報
RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID", "").strip()
RAKUTEN_ACCESS_KEY = os.getenv("RAKUTEN_ACCESS_KEY", "").strip()

if not RAKUTEN_APP_ID or not RAKUTEN_ACCESS_KEY:
    raise ValueError("RAKUTEN_APP_ID / RAKUTEN_ACCESS_KEY が .env にありません")

# 楽天市場APIエンドポイント（新ドメイン）
ICHIBA_ITEM_SEARCH_URL = (
    "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20220601"
)

# 共通リクエスト設定
REQUEST_TIMEOUT = 20
DEFAULT_HITS = 30          # 1回で何件取るか
MAX_PAGES_PER_KEYWORD = 3  # キーワードごとに回すページ数

# ROOM向けフィルタ閾値
MIN_REVIEW_AVG = 4.2
MIN_REVIEW_COUNT = 300
MIN_PRICE = 1500
MAX_PRICE = 10000
MIN_AFFILIATE_RATE = 3.0