# processors/normalize.py

from datetime import datetime
from typing import Dict, Any


def normalize_item(
    raw: Dict[str, Any],
    source: str,
    main_genre: str,
    sub_genre: str,
    keyword: str,
) -> Dict[str, Any]:
    """Rakuten APIの1アイテムを共通カラムに整形。"""
    item = raw

    medium_images = item.get("mediumImageUrls") or []
    image_url = medium_images[0] if medium_images else None

    return {
        "collected_at": datetime.now().isoformat(timespec="seconds"),
        "source": source,
        "main_genre": main_genre,
        "sub_genre": sub_genre,
        "keyword": keyword,
        "item_code": item.get("itemCode"),
        "item_name": item.get("itemName"),
        "item_price": item.get("itemPrice"),
        "shop_name": item.get("shopName"),
        "shop_code": item.get("shopCode"),
        "review_average": item.get("reviewAverage"),
        "review_count": item.get("reviewCount"),
        "affiliate_rate": item.get("affiliateRate"),
        "point_rate": item.get("pointRate"),
        "point_rate_start": item.get("pointRateStartTime"),
        "point_rate_end": item.get("pointRateEndTime"),
        "item_url": item.get("itemUrl"),
        "image_url": image_url,
        "availability": item.get("availability"),
        "score": 0,
    }