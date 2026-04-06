# processors/score.py

from typing import Dict, Any


def score_row(row: Dict[str, Any]) -> int:
    score = 0

    price = int(row.get("item_price") or 0)
    review_avg = float(row.get("review_average") or 0.0)
    review_count = int(row.get("review_count") or 0)
    affiliate_rate = float(row.get("affiliate_rate") or 0.0)
    point_rate = int(row.get("point_rate") or 0)
    source = row.get("source") or ""
    name = (row.get("item_name") or "").lower()

    # レビュー平均
    if review_avg >= 4.5:
        score += 25
    elif review_avg >= 4.2:
        score += 18
    elif review_avg >= 4.0:
        score += 10
    else:
        score -= 10

    # レビュー件数
    if review_count >= 2000:
        score += 25
    elif review_count >= 1000:
        score += 18
    elif review_count >= 300:
        score += 10
    elif review_count >= 100:
        score += 5

    # 価格帯
    if 3000 <= price <= 10000:
        score += 15
    elif 1500 <= price <= 10000:
        score += 8
    else:
        score -= 5

    # アフィリエイト率
    if affiliate_rate >= 4.0:
        score += 12
    elif affiliate_rate >= 3.0:
        score += 8
    elif affiliate_rate >= 2.0:
        score += 3

    # ポイント倍率
    # 楽天APIでは pointRate は 2〜10 が有効値として返る案内があり、
    # 倍率情報がない商品は 1 や空になることがあります。
    if point_rate >= 10:
        score += 12
    elif point_rate >= 5:
        score += 8
    elif point_rate >= 2:
        score += 4

    # ランキング由来なら加点（今後 ranking 追加時に効く）
    if source == "ranking":
        score += 15

    # ガジェット系っぽいキーワード
    positive_keywords = [
        "usb-c",
        "pd",
        "gan",
        "急速充電",
        "折りたたみ",
        "静音",
        "省スペース",
        "コンパクト",
        "エルゴノミクス",
        "ワイヤレス",
        "ケーブル内蔵",
        "軽量",
    ]
    score += sum(3 for k in positive_keywords if k in name)

    return score