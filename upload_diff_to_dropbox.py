# upload_diff_to_dropbox.py

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import dropbox

from config import OUTPUT_DIR

# Dropbox パスのベース
DROPBOX_BASE_PATH = "/daily-auto-post-bot/rakuten"


def load_latest_dropbox_csv(dbx: dropbox.Dropbox) -> pd.DataFrame | None:
    """
    Dropbox上の /daily-auto-post-bot/rakuten/ にある
    最新の *_items.xlsx から candidate_items シートを読む想定もできるが、
    まずは「最新の candidate_items.csv があれば読む」くらいの運用にしておく。
    （必要になったら履歴管理を拡張）
    """
    # 今回はシンプルに「前回の candidate_items.csv をローカルに残しておき、
    # それがあればそれを読む」運用にする。
    prev_path = OUTPUT_DIR / "prev_candidate_items.csv"
    if not prev_path.exists():
        return None
    return pd.read_csv(prev_path)


def save_current_as_prev():
    """今回の candidate_items.csv を prev_candidate_items.csv として保存。"""
    curr = OUTPUT_DIR / "candidate_items.csv"
    prev = OUTPUT_DIR / "prev_candidate_items.csv"
    if curr.exists():
        curr.replace(prev)


def build_diff_df(prev: pd.DataFrame | None, curr: pd.DataFrame) -> pd.DataFrame:
    """
    前回と今回の candidate_items を比較して差分を作る。
    - new: 今回のみ
    - dropped: 前回のみ（今回は不要なので一旦スキップも可）
    - changed: score が変わったもの など
    まずは new だけで良い、とのことなので new だけ出す。
    """
    if prev is None:
        # 初回は全件 new として扱う
        diff = curr.copy()
        diff["diff_type"] = "new"
        return diff

    key = "item_code"
    if key not in curr.columns or key not in prev.columns:
        raise ValueError("item_code 列がありません")

    prev_codes = set(prev[key].astype(str))
    curr_codes = set(curr[key].astype(str))

    new_codes = curr_codes - prev_codes

    diff = curr[curr[key].astype(str).isin(new_codes)].copy()
    diff["diff_type"] = "new"
    return diff


def upload_excel_to_dropbox(diff_df: pd.DataFrame, dbx: dropbox.Dropbox):
    """差分DFをExcelにしてDropboxにアップロード。"""
    today = datetime.now().strftime("%Y%m%d")
    diff_count = len(diff_df)
    filename = f"{today}_{diff_count:02d}items.xlsx"

    # ローカルに一時的に保存
    tmp_path = OUTPUT_DIR / filename
    tmp_path.parent.mkdir(exist_ok=True)

    # Excelへ書き出し
    with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:
        diff_df.to_excel(writer, index=False, sheet_name="diff")

    dropbox_path = f"{DROPBOX_BASE_PATH}/{filename}"

    with tmp_path.open("rb") as f:
        dbx.files_upload(
            f.read(),
            dropbox_path,
            mode=dropbox.files.WriteMode("overwrite"),
            mute=True,
        )

    print(f"[INFO] uploaded diff to Dropbox: {dropbox_path}")

    # 必要ならローカルの一時ファイルは残しておいてもOK
    # tmp_path.unlink(missing_ok=True)


def main():
    token = os.getenv("DROPBOX_ACCESS_TOKEN")
    if not token:
        raise ValueError("DROPBOX_ACCESS_TOKEN が環境変数にありません")

    curr_path = OUTPUT_DIR / "candidate_items.csv"
    if not curr_path.exists():
        print("[WARN] candidate_items.csv not found, skip diff/upload")
        return

    curr_df = pd.read_csv(curr_path)

    dbx = dropbox.Dropbox(token)

    # 前回データを取得（シンプルにローカル prev_* を使う）
    prev_df = load_latest_dropbox_csv(dbx)

    # 差分DFを作成
    diff_df = build_diff_df(prev_df, curr_df)

    # Dropboxへアップロード
    upload_excel_to_dropbox(diff_df, dbx)

    # 今回のデータを prev として保存
    save_current_as_prev()


if __name__ == "__main__":
    main()