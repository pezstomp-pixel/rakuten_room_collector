from pathlib import Path
import os
from dotenv import load_dotenv

# ベースディレクトリ
BASE_DIR = Path(__file__).resolve().parent

# .env 読み込み（ローカル用）
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

# 出力ディレクトリ
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 楽天APIの認証情報
# 1. GitHub Actions の Secrets（環境変数）を優先
# 2. なければ、従来どおり .env の RAKUTEN_APP_ID / RAKUTEN_ACCESS_KEY を使う
RAKUTEN_APP_ID = (
    os.getenv("RAKUTEN_APPLICATION_ID")  # Actions 用
    or os.getenv("RAKUTEN_APP_ID")       # .env 用
)
RAKUTEN_ACCESS_KEY = (
    os.getenv("RAKUTEN_AFFILIATE_ID")    # Actions 用（Affiliate ID）
    or os.getenv("RAKUTEN_ACCESS_KEY")   # .env 用
)

RAKUTEN_APP_ID = (RAKUTEN_APP_ID or "").strip()
RAKUTEN_ACCESS_KEY = (RAKUTEN_ACCESS_KEY or "").strip()

if not RAKUTEN_APP_ID or not RAKUTEN_ACCESS_KEY:
    raise ValueError("RAKUTEN_APP_ID / RAKUTEN_ACCESS_KEY が 環境変数または .env にありません")

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