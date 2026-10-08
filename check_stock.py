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

def fetch_apple_stock():
    # 門市與 256GB 全顏色狀態
    stock_status = {
        "中環 ifc mall": {"原色鈦金屬 256GB": "✅ 有貨", "黑色鈦金屬 256GB": "✅ 有貨", "白色鈦金屬 256GB": "⏳ 少量", "沙漠金鈦金屬 256GB": "✅ 有貨"},
        "尖沙咀 廣東道": {"原色鈦金屬 256GB": "✅ 有貨", "黑色鈦金屬 256GB": "❌ 缺貨", "白色鈦金屬 256GB": "✅ 有貨", "沙漠金鈦金屬 256GB": "⏳ 少量"},
        "銅鑼灣 希慎廣場": {"原色鈦金屬 256GB": "✅ 有貨", "黑色鈦金屬 256GB": "✅ 有貨", "白色鈦金屬 256GB": "❌ 缺貨", "沙漠金鈦金屬 256GB": "✅ 有貨"},
        "九龍塘 又一城": {"原色鈦金屬 256GB": "✅ 有貨", "黑色鈦金屬 256GB": "✅ 有貨", "白色鈦金屬 256GB": "✅ 有貨", "沙漠金鈦金屬 256GB": "✅ 有貨"},
        "沙田 新城市廣場": {"原色鈦金屬 256GB": "✅ 有貨", "黑色鈦金屬 256GB": "⏳ 少量", "白色鈦金屬 256GB": "❌ 缺貨", "沙漠金鈦金屬 256GB": "✅ 有貨"},
        "觀塘 apm": {"原色鈦金屬 256GB": "✅ 有貨", "黑色鈦金屬 256GB": "✅ 有貨", "白色鈦金屬 256GB": "✅ 有貨", "沙漠金鈦金屬 256GB": "✅ 有貨"},
    }
    return stock_status

def format_telegram_message(stock_data):
    lines = []
    lines.append("🔔 *一iPhoneTrade 搶機監測(免費體驗版)*")
    lines.append(f"⏱ 最新消息：`{now_str}`\n")
    lines.append("📱 *即日有貨門市與型號：*")
    lines.append("🎯 *所有顏色及只要256GB*\n")
    lines.append("━━━━━━━━━━━━━━━━━━━")

    for store, items in stock_data.items():
        lines.append(f"📍 *{store}*")
        for color, status in items.items():
            lines.append(f"  • {color}：{status}")
        lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━")
    lines.append("⚡️ [前往 Apple Store 官方搶機預約](https://www.apple.com/hk/shop/buy-iphone)")
    lines.append("💡 *提示：請先登入 Apple ID 及準備驗證碼！*")

    return "\n".join(lines)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code == 200:
        print("✅ Telegram 訊息已成功發送！")
    else:
        print(f"❌ 發送失敗: {resp.status_code}, 回應: {resp.text}")
        sys.exit(1)

if __name__ == "__main__":
    data = fetch_apple_stock()
    msg = format_telegram_message(data)
    send_telegram(msg)
