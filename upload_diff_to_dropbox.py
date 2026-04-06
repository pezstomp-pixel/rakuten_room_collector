# upload_diff_to_dropbox.py

import os
from datetime import datetime
from pathlib import Path

import dropbox
import pandas as pd

# config.py を import しない
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

DROPBOX_BASE_PATH = "/daily-auto-post-bot/rakuten"


def load_previous_candidate() -> pd.DataFrame | None:
    prev_path = OUTPUT_DIR / "prev_candidate_items.csv"
    if not prev_path.exists():
        return None
    return pd.read_csv(prev_path)


def save_current_as_previous():
    curr_path = OUTPUT_DIR / "candidate_items.csv"
    prev_path = OUTPUT_DIR / "prev_candidate_items.csv"
    if curr_path.exists():
        prev_path.write_bytes(curr_path.read_bytes())


def build_diff_df(prev_df: pd.DataFrame | None, curr_df: pd.DataFrame) -> pd.DataFrame:
    # 初回は全件 new
    if prev_df is None:
        diff_df = curr_df.copy()
        diff_df["diff_type"] = "new"
        return diff_df

    key = "item_code"
    if key not in prev_df.columns or key not in curr_df.columns:
        raise ValueError("item_code 列がありません")

    prev_codes = set(prev_df[key].astype(str))
    curr_codes = set(curr_df[key].astype(str))

    new_codes = curr_codes - prev_codes

    diff_df = curr_df[curr_df[key].astype(str).isin(new_codes)].copy()
    diff_df["diff_type"] = "new"
    return diff_df


def upload_excel_to_dropbox(diff_df: pd.DataFrame, dbx: dropbox.Dropbox):
    today = datetime.now().strftime("%Y%m%d")
    diff_count = len(diff_df)
    filename = f"{today}_{diff_count}items.xlsx"

    local_excel_path = OUTPUT_DIR / filename

    with pd.ExcelWriter(local_excel_path, engine="openpyxl") as writer:
        diff_df.to_excel(writer, index=False, sheet_name="diff")

    dropbox_path = f"{DROPBOX_BASE_PATH}/{filename}"

    with open(local_excel_path, "rb") as f:
        dbx.files_upload(
            f.read(),
            dropbox_path,
            mode=dropbox.files.WriteMode.overwrite,
        )

    print(f"[INFO] uploaded: {dropbox_path}")


def main():
    token = os.getenv("DROPBOX_ACCESS_TOKEN", "").strip()
    if not token:
        raise ValueError("DROPBOX_ACCESS_TOKEN がありません")

    curr_path = OUTPUT_DIR / "candidate_items.csv"
    if not curr_path.exists():
        raise ValueError("output/candidate_items.csv がありません")

    curr_df = pd.read_csv(curr_path)
    prev_df = load_previous_candidate()

    diff_df = build_diff_df(prev_df, curr_df)

    dbx = dropbox.Dropbox(token)
    upload_excel_to_dropbox(diff_df, dbx)

    save_current_as_previous()


if __name__ == "__main__":
    main()