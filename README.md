# iPhone Duo 香港 Apple Store 店內取貨監測（Telegram）

此版本監測 Apple 香港網站公布的 iPhone Duo 全部 8 個顏色／容量組合，以及各 Apple Store 店內取貨狀態；偵測到新的有貨組合時，會透過 Telegram Bot 發送通知。**不使用 WhatsApp 或 Green-API。**

## 安裝到 `carjj/iphone18-stock-monitor`

將本資料夾中的 `check_stock.py`、`.github/workflows/stock_alert.yml` 和此 README 複製到 repo 根目錄，覆蓋同名檔案。到 GitHub repo **Settings → Secrets and variables → Actions → New repository secret** 設定：

| Secret 名稱 | 值 |
|---|---|
| `TG_BOT_TOKEN` | 你的 Telegram Bot Token（只存於 GitHub Secret，不要寫進程式碼或貼在聊天裡） |
| `TG_CHAT_ID` | 接收通知的 Telegram chat ID |

若原 repo 已設定 `TG_BOT_TOKEN`、`TG_CHAT_ID`，可沿用現有 Secrets；請確認值正確、Bot 已能向該 chat 發訊息。

## 啟用

1. 到 repo **Settings → Actions → General → Workflow permissions**，允許 workflow 讀寫 repository（`contents: write`）。
2. 到 **Actions** 頁面啟用 workflows。
3. 手動執行一次 **iPhone Duo Apple HK Pickup Monitor** workflow 作測試；之後排程約每 5 分鐘查一次。

GitHub Actions 的排程不是秒級即時，忙碌時可能延遲。Apple 亦可能限流或更改庫存查詢介面；如 Apple 回應錯誤，本程式會讓該次 workflow 失敗，不會將查詢錯誤當成缺貨。

## 監測組合

| SKU | 顏色 | 容量 |
|---|---|---:|
| MK2D4ZA/A | 星光白色 | 256GB |
| MK2E4ZA/A | 夜空色 | 256GB |
| MK2F4ZA/A | 星光白色 | 512GB |
| MK2G4ZA/A | 夜空色 | 512GB |
| MK2H4ZA/A | 星光白色 | 1TB |
| MK2J4ZA/A | 夜空色 | 1TB |
| MK2K4ZA/A | 星光白色 | 2TB |
| MK2L4ZA/A | 夜空色 | 2TB |
