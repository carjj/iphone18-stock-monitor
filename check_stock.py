import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

HKT = timezone(timedelta(hours=8))
APPLE_URL = "https://www.apple.com/hk-zh/shop/fulfillment-messages"

# Apple 香港官網產品選項 SKU，從每個容量／顏色選項頁提取。
PRODUCTS = {
    "MK2D4ZA/A": ("星光白色", "256GB"),
    "MK2E4ZA/A": ("夜空色", "256GB"),
    "MK2F4ZA/A": ("星光白色", "512GB"),
    "MK2G4ZA/A": ("夜空色", "512GB"),
    "MK2H4ZA/A": ("星光白色", "1TB"),
    "MK2J4ZA/A": ("夜空色", "1TB"),
    "MK2K4ZA/A": ("星光白色", "2TB"),
    "MK2L4ZA/A": ("夜空色", "2TB"),
}
STATE_FILE = Path("stock_state.json")


def env(name, default=None):
    return os.environ.get(name, default)


def check_stock():
    params = {
        "pl": "true",
        "mts.0": "regular",
        "location": "Hong Kong",
    }
    params.update({f"parts.{i}": sku for i, sku in enumerate(PRODUCTS)})
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; iPhoneDuoStockMonitor/1.0)",
        "Referer": "https://www.apple.com/hk-zh/shop/buy-iphone/iphone-duo",
        "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
    }
    response = requests.get(APPLE_URL, params=params, headers=headers, timeout=25)
    response.raise_for_status()
    data = response.json()
    stores = data.get("body", {}).get("stores", [])
    if not stores:
        raise RuntimeError("Apple 回應沒有分店資料；停止本輪，避免把查詢失敗誤報為缺貨。")

    found = {}
    for store in stores:
        store_name = store.get("storeName", "未知分店")
        availability = store.get("partsAvailability", {})
        for sku, (color, capacity) in PRODUCTS.items():
            detail = availability.get(sku, {})
            # 只有 Apple 明確回報 available 才當作有貨。
            if detail.get("pickupDisplay") == "available":
                found[f"{store_name}|{color}|{capacity}"] = {
                    "store": store_name,
                    "color": color,
                    "capacity": capacity,
                    "sku": sku,
                    "url": f"https://www.apple.com/hk-zh/shop/buy-iphone/iphone-duo/7.6-%E5%90%8B%E9%A1%AF%E7%A4%BA%E5%99%A8-{capacity.lower()}-{color}",
                }
    return found


def send_telegram(message):
    bot_token = env("TG_BOT_TOKEN")
    chat_id = env("TG_CHAT_ID")
    if not bot_token or not chat_id:
        raise RuntimeError("缺少 TG_BOT_TOKEN 或 TG_CHAT_ID；請在 GitHub Actions Secrets 設定，勿寫入程式碼。")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": message, "disable_web_page_preview": True},
        timeout=20,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(f"Telegram 未確認訊息已送出：{result}")


def read_state():
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"available": []}


def main():
    available = check_stock()
    current = sorted(available)
    previous = read_state().get("available", [])
    newly_available = [key for key in current if key not in previous]

    now = datetime.now(HKT).strftime("%Y-%m-%d %H:%M:%S HKT")
    print(f"[{now}] Apple 香港：查到 {len(current)} 個有貨的分店／配置組合")
    for key in current:
        print("有貨：", key)

    if newly_available:
        lines = ["📱 iPhone Duo Apple 香港店內取貨有貨！", f"檢查時間：{now}", ""]
        for key in newly_available:
            item = available[key]
            lines.append(f"✅ {item['store']}｜{item['color']}｜{item['capacity']}")
            lines.append(item["url"])
        send_telegram("\n".join(lines))
        print(f"已通知 Telegram：新增 {len(newly_available)} 項有貨。")
    elif not current:
        print("目前沒有查到有貨；沒有發送通知。")

    STATE_FILE.write_text(json.dumps({"available": current}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"監測失敗：{exc}", file=sys.stderr)
        sys.exit(1)
