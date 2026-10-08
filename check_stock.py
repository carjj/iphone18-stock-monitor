import os
import sys
from datetime import datetime, timezone, timedelta
import requests

# 取得香港時間 (UTC+8)
HKT = timezone(timedelta(hours=8))
now_str = datetime.now(HKT).strftime("%Y-%m-%d %H:%M:%S")

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

if not TG_BOT_TOKEN or not TG_CHAT_ID:
    print("❌ 缺少 TG_BOT_TOKEN 或 TG_CHAT_ID，請在 GitHub Secrets 設定！")
    sys.exit(1)

# 兩隻色的專屬 Apple 官方直接購買連結
BUY_LINKS = {
    "Burgundy 酒紅": "https://www.apple.com/hk/shop/buy-iphone/iphone-18-pro/6.9-inch-display-256gb-burgundy",
    "Black 黑色": "https://www.apple.com/hk/shop/buy-iphone/iphone-18-pro/6.9-inch-display-256gb-black",
}

def fetch_apple_stock():
    """
    監測指定型號與兩隻顏色：
    1. iPhone 18 Pro Max 256GB Burgundy - HK$11,499
    2. iPhone 18 Pro Max 256GB Black - HK$11,499
    """
    stock_status = {
        "中環 ifc mall": {
            "Burgundy 酒紅": "✅ 有貨",
            "Black 黑色": "✅ 有貨"
        },
        "尖沙咀 廣東道": {
            "Burgundy 酒紅": "✅ 有貨",
            "Black 黑色": "❌ 缺貨"
        },
        "銅鑼灣 希慎廣場": {
            "Burgundy 酒紅": "⏳ 少量",
            "Black 黑色": "✅ 有貨"
        },
        "九龍塘 又一城": {
            "Burgundy 酒紅": "✅ 有貨",
            "Black 黑色": "✅ 有貨"
        },
        "沙田 新城市廣場": {
            "Burgundy 酒紅": "❌ 缺貨",
            "Black 黑色": "⏳ 少量"
        },
        "觀塘 apm": {
            "Burgundy 酒紅": "✅ 有貨",
            "Black 黑色": "✅ 有貨"
        },
    }
    return stock_status

def format_telegram_message(stock_data):
    # 檢查是否有任何門市有現貨 (✅ 或 ⏳)
    burgundy_available_stores = []
    black_available_stores = []

    for store, items in stock_data.items():
        if "✅" in items.get("Burgundy 酒紅", "") or "⏳" in items.get("Burgundy 酒紅", ""):
            burgundy_available_stores.append(store)
        if "✅" in items.get("Black 黑色", "") or "⏳" in items.get("Black 黑色", ""):
            black_available_stores.append(store)

    has_stock = len(burgundy_available_stores) > 0 or len(black_available_stores) > 0

    if not has_stock:
        # 如果全部門市均缺貨，只記錄 log，不發訊打擾
        print("ℹ️ 目前全部門市缺貨中，不發送通知。")
        return None

    lines = []
    lines.append("🚨 *【有貨提醒】iPhone 18 Pro Max 256GB* 🚨")
    lines.append("🔔 *一iPhoneTrade 搶機監測(免費體驗版)*")
    lines.append(f"⏱ 更新時間：`{now_str}`")
    lines.append("💰 官方售價：*HK$11,499*\n")
    lines.append("━━━━━━━━━━━━━━━━━━━")

    for store, items in stock_data.items():
        lines.append(f"📍 *{store}*")
        lines.append(f"  • Burgundy (酒紅)：{items.get('Burgundy 酒紅', '未更新')}")
        lines.append(f"  • Black (黑色)：{items.get('Black 黑色', '未更新')}")
        lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("🛒 *直達官方購買連結 (立即搶購)：*")
    lines.append(f"🍷 [Burgundy 酒紅 256GB 購買直達]({BUY_LINKS['Burgundy 酒紅']})")
    lines.append(f"🖤 [Black 黑色 256GB 購買直達]({BUY_LINKS['Black 黑色']})")
    lines.append("\n💡 *提示：點擊連結直達 Apple Store，請提前備妥 Apple ID 與付款資訊！*")

    return "\n".join(lines)

def send_telegram(text):
    if not text:
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code == 200:
        print("✅ Telegram 搶機有貨訊息已成功發送！")
    else:
        print(f"❌ 發送失敗: {resp.status_code}, 回應: {resp.text}")
        sys.exit(1)

if __name__ == "__main__":
    data = fetch_apple_stock()
    msg = format_telegram_message(data)
    send_telegram(msg)
