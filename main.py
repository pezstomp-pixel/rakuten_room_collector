# main.py

import pandas as pd

from keywords import GENRE_KEYWORDS
from collectors.item_search import fetch_search_items
from processors.normalize import normalize_item
from processors.score import score_row
from config import (
    OUTPUT_DIR,
    MIN_REVIEW_AVG,
    MIN_REVIEW_COUNT,
    MIN_PRICE,
    MAX_PRICE,
    MIN_AFFILIATE_RATE,
)

# 出力列の順番（CSV / XLSX 共通）
OUTPUT_COLUMNS = [
    "collected_at",
    "source",
    "main_genre",
    "sub_genre",
    "keyword",
    "item_code",
    "item_price",
    "shop_name",
    "shop_code",
    "availability",
    "review_average",
    "score",
    "review_count",
    "affiliate_rate",
    "point_rate",
    "point_rate_start",
    "point_rate_end",
    "image_url",
    "item_name",
    "item_url",
]


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """OUTPUT_COLUMNS の順に並べ替え、足りない列は空列で補完。"""
    existing = [c for c in OUTPUT_COLUMNS if c in df.columns]
    missing = [c for c in OUTPUT_COLUMNS if c not in df.columns]

    for c in missing:
        df[c] = ""

    return df[OUTPUT_COLUMNS].copy()


def build_dataset():
    rows = []

    for main_genre, sub_map in GENRE_KEYWORDS.items():
        for sub_genre, keywords in sub_map.items():
            for kw in keywords:
                print(f"[INFO] fetch: {main_genre} / {sub_genre} / {kw}")
                items = fetch_search_items(kw)

                for raw in items:
                    rows.append(
                        normalize_item(
                            raw=raw,
                            source="search",
                            main_genre=main_genre,
                            sub_genre=sub_genre,
                            keyword=kw,
                        )
                    )

    if not rows:
        print("[WARN] no items collected")
        return

    df = pd.DataFrame(rows)

    # 重複除去
    df = df.drop_duplicates(subset=["item_code"]).copy()

    # 型を整える
    numeric_int_cols = ["item_price", "review_count", "point_rate", "score", "availability"]
    numeric_float_cols = ["review_average", "affiliate_rate"]

    for col in numeric_int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in numeric_float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(float)

    # スコア計算
    df["score"] = df.apply(lambda r: score_row(r.to_dict()), axis=1)

    # 念のため、失敗した説明文取得系の列が残っていたら落とす
    drop_cols = [
        "catchcopy",
        "item_caption_raw",
        "item_caption_clean",
        "item_caption_short",
        "caption_fetched",
    ]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    # 列順を固定（raw 用）
    df = reorder_columns(df)

    # raw 出力
    raw_path = OUTPUT_DIR / "raw_items.csv"
    df.to_csv(raw_path, index=False, encoding="utf-8-sig")
    print("[INFO] wrote:", raw_path)
    print("[INFO] raw items:", len(df))

    # candidate 抽出
    cand = df[
        (df["review_average"] >= MIN_REVIEW_AVG)
        & (df["review_count"] >= MIN_REVIEW_COUNT)
        & (df["item_price"].between(MIN_PRICE, MAX_PRICE))
        & (df["affiliate_rate"] >= MIN_AFFILIATE_RATE)
    ].copy()

    # candidate 並び順
    cand = cand.sort_values(
        ["score", "point_rate", "review_count", "review_average"],
        ascending=[False, False, False, False],
    )

    # 念のため candidate 側でも不要列を落とす
    cand = cand.drop(columns=[c for c in drop_cols if c in cand.columns], errors="ignore")

    # 列順を固定（candidate 用）
    cand = reorder_columns(cand)

    # candidate CSV 出力
    cand_csv_path = OUTPUT_DIR / "candidate_items.csv"
    cand.to_csv(cand_csv_path, index=False, encoding="utf-8-sig")
    print("[INFO] wrote:", cand_csv_path)
    print("[INFO] candidates:", len(cand))

    # candidate XLSX 出力（同じ列順）
    cand_xlsx_path = OUTPUT_DIR / "candidate_items.xlsx"
    cand.to_excel(cand_xlsx_path, index=False)
    print("[INFO] wrote:", cand_xlsx_path)

    # 確認用に上位10件を表示
    preview_cols = [
        "main_genre",
        "sub_genre",
        "item_name",
        "item_price",
        "review_average",
        "review_count",
        "affiliate_rate",
        "point_rate",
        "score",
    ]

    available_preview_cols = [c for c in preview_cols if c in cand.columns]

    if len(cand) > 0:
        print("\n[INFO] top candidates:")
        print(cand[available_preview_cols].head(10).to_string(index=False))
    else:
        print("[INFO] no candidates after filtering")


if __name__ == "__main__":
    build_dataset()