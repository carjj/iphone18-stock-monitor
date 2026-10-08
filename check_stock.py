import os
import sys
import requests
from datetime import datetime, timezone, timedelta

# 香港時間 (UTC+8)
HKT = timezone(timedelta(hours=8))
now_str = datetime.now(HKT).strftime("%Y-%m-%d %H:%M:%S")

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

if not TG_BOT_TOKEN or not TG_CHAT_ID:
    print("❌ 缺少 TG_BOT_TOKEN 或 TG_CHAT_ID，請在 GitHub Secrets 設定！")
    sys.exit(1)

# Apple 官方精確 SKU (香港港版 ZA/A)
PRODUCTS = {
    "MJXQ4ZA/A": {
        "name": "Burgundy 酒紅 256GB",
        "url": "https://www.apple.com/hk/shop/buy-iphone/iphone-18-pro/6.9-inch-display-256gb-burgundy"
    },
    "MJXN4ZA/A": {
        "name": "Black 黑色 256GB",
        "url": "https://www.apple.com/hk/shop/buy-iphone/iphone-18-pro/6.9-inch-display-256gb-black"
    }
}

# 香港 Apple 直營店中英文對應
STORE_NAMES = {
    "ifc mall": "中環 ifc mall",
    "Canton Road": "尖沙咀 廣東道",
    "Causeway Bay": "銅鑼灣 希慎廣場",
    "Festival Walk": "九龍塘 又一城",
    "New Town Plaza": "沙田 新城市廣場",
    "apm Hong Kong": "觀塘 apm"
}

def check_real_apple_stock():
    """
    直接向 Apple 香港官方零售庫存 API 請求即時真實數據
    """
    url = "https://www.apple.com/hk/shop/retail/pickup-message"
    params = {
        "pl": "true",
        "mts.0": "regular",
        "location": "Hong Kong",
        "parts.0": "MJXQ4ZA/A",
        "parts.1": "MJXN4ZA/A"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.apple.com/hk/shop/buy-iphone/iphone-18-pro"
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"❌ Apple API 請求失敗，HTTP 狀態碼: {resp.status_code}")
            return None, False

        data = resp.json()
        stores = data.get("body", {}).get("stores", [])
        
        results = {}
        has_any_stock = False

        for store in stores:
            raw_name = store.get("storeName", "")
            store_display = STORE_NAMES.get(raw_name, raw_name)
            results[store_display] = {}

            parts_avail = store.get("partsAvailability", {})
            for part_id, p_info in PRODUCTS.items():
                sku_data = parts_avail.get(part_id, {})
                pickup_display = sku_data.get("pickupDisplay", "unavailable")

                # 只有 Apple 官方顯示 available 時才代表真實能落單取貨
                if pickup_display == "available":
                    status = "✅ 即日有貨"
                    has_any_stock = True
                else:
                    status = "❌ 缺貨"

                results[store_display][p_info["name"]] = status

        return results, has_any_stock

    except Exception as e:
        print(f"❌ 查詢 Apple 官方庫存出錯: {e}")
        return None, False

def format_telegram_message(stock_results):
    lines = []
    lines.append("🚨 *【Apple 官方真實現貨提醒】* 🚨")
    lines.append("🔔 *一iPhoneTrade 搶機監測(即時真實庫存)*")
    lines.append(f"⏱ 監測時間：`{now_str}`")
    lines.append("📱 *型號：iPhone 18 Pro Max 256GB*")
    lines.append("💰 官方定價：*HK$11,499*\n")
    lines.append("━━━━━━━━━━━━━━━━━━━")

    for store, items in stock_results.items():
        lines.append(f"📍 *{store}*")
        for prod_name, status in items.items():
            lines.append(f"  • {prod_name}：{status}")
        lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("🛒 *官方直達搶購連結 (立即購買)：*")
    lines.append(f"🍷 [Burgundy 酒紅 256GB 官方購買直達]({PRODUCTS['MJXQ4ZA/A']['url']})")
    lines.append(f"🖤 [Black 黑色 256GB 官方購買直達]({PRODUCTS['MJXN4ZA/A']['url']})")
    lines.append("\n⚡️ *Apple 現貨隨時被秒殺，點擊連結直達結帳！*")

    return "\n".join(lines)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code == 200:
        print("✅ Telegram 庫存通知已成功發送！")
    else:
        print(f"❌ Telegram 發送失敗: {resp.status_code}, {resp.text}")

if __name__ == "__main__":
    stock_results, has_stock = check_real_apple_stock()

    if not stock_results:
        print("無法取得 Apple 官方數據。")
        sys.exit(1)

    print(f"[{now_str}] 查詢成功！是否有現貨: {has_stock}")

    # 「有貨先提醒」：只有當 Apple 官方回傳有貨或手動強制測試時才推播
    force_send = os.environ.get("FORCE_SEND", "false").lower() == "true"
    if has_stock or force_send:
        msg = format_telegram_message(stock_results)
        send_telegram(msg)
    else:
        print("全港 6 間 Apple Store 目前真實狀態為缺貨中，不打擾發送 Telegram。")
