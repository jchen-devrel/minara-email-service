# minara-email-service 項目梳理

## 一、項目簡介

這是一個基於 **Mailgun** 的批量郵件發送服務，用於 Minara 及 NFTGo 等品牌的郵件營銷活動。支援個人化模板、分批發送、斷點續傳、退訂管理等功能。

---

## 二、與 Mailgun 的結合方式

### 2.1 兩種發送方式

本項目支援兩種與 Mailgun 整合的方式：

| 方式 | 說明 | 配置項 | 使用場景 |
|------|------|--------|----------|
| **SMTP** | 透過 `smtp.mailgun.org:587` 發送 | `smtp_username`、`smtp_password` | 簡單發送、無需追蹤 |
| **Mailgun API** | 直接調用 `api.mailgun.net/v3/{domain}/messages` | `mailgun_domain`、`mailgun_api_key` | 開信追蹤、標籤、退訂過濾、One-Click Unsubscribe |

### 2.2 所需 Mailgun 憑證

從 **Mailgun Dashboard → Sending → Domain** 和 **Settings → API Keys** 取得：

```python
# config.py 中需要填寫
MINARA_CONFIG = {
    # SMTP 用（若用 API 發送，可選填）
    'smtp_username': 'postmaster@minara.ai',           # 發送域名下的 SMTP 用戶名
    'smtp_password': 'xxx',                            # Sending → Domain → SMTP credentials
    'from_email': 'hello@minara.ai',                   # 發件人郵箱（須在 Mailgun 域名下驗證）
    'from_name': 'Minara Team',                         # 發件人顯示名稱
    'delay_between_emails': 20,                         # 每封間隔秒數（建議 20 避免觸發限速）
    
    # API 用（minara_campaign 和 batch_campaign 預設走 API）
    'mailgun_domain': 'minara.ai',                     # Sending Domain
    'mailgun_api_key': 'key-xxxxxxxxxxxx',             # Settings → API Keys → Private API key
}
```

### 2.3 發送流程（API 模式）

```
用戶 JSON → 退訂過濾（UnsubscribeManager）→ 逐封個人化模板
         → POST https://api.mailgun.net/v3/{domain}/messages
         → 開信追蹤、標籤、List-Unsubscribe 等由 Mailgun 處理
```

### 2.4 核心 Mailgun 功能使用情況

| 功能 | 是否使用 | 位置 |
|------|----------|------|
| 開信追蹤（Tracking Opens） | ✅ | `email_sender.py` `o:tracking-opens` |
| 點擊追蹤（Clicks） | ❌ 關閉 | 避免 URL rewrite 問題 |
| 標籤（Tags） | ✅ | `--tags` 參數，用於 Mailgun 統計 |
| 退訂列表過濾 | ✅ | `UnsubscribeManager.filter_user_list()` |
| List-Unsubscribe / One-Click | ✅ | RFC 2369、RFC 8058 標頭 |
| TLS 強制 | ✅ | `o:require-tls: yes` |

---

## 三、目錄結構與職責

```
minara-email-service/
├── config.example.py          # 配置模板（複製為 config.py 並填寫）
├── config.py                  # 實際憑證（gitignore）
├── requirements.txt           # requests, python-dotenv
│
├── src/
│   ├── email_sender.py        # 統一郵件發送器（SMTP + Mailgun API）
│   ├── unsubscribe_manager.py # 退訂列表管理（查詢/過濾/添加）
│   ├── convert_txt_to_json.py # txt → json 用戶列表
│   ├── convert_csv_to_json.py # csv → json
│   └── convert_excel_to_json.py # excel → json
│
├── campaigns/
│   ├── minara_campaign.py     # Minara 單次發送（走 Mailgun API）
│   ├── batch_campaign.py      # 大列表分批發送（可斷點續傳）
│   ├── nftgo_campaign.py      # NFTGo 營銷（走 SMTP，需 NFTGO_CONFIG）
│   └── minara/progress/       # 分批發送進度檔
│
├── templates/
│   ├── minara/*.html          # Minara 郵件模板
│   └── nftgo/*.html           # NFTGo 郵件模板
│
├── data/
│   ├── minara/*.json          # Minara 用戶列表
│   └── nftgo/*.json           # NFTGo 用戶列表
│
└── serve_templates.py         # 本地預覽模板（http://localhost:8000）
```

---

## 四、你可以做的改動

### 4.1 配置與環境

| 改動 | 說明 |
|------|------|
| **新增品牌配置** | 在 `config.py` 增加 `NFTGO_CONFIG` 等，結構同 `MINARA_CONFIG` |
| **替換發送方式** | 在 campaign 腳本中改 `method='smtp'` 或 `method='api'` |
| **調整發送速率** | 修改 `delay_between_emails` 或 `batch_campaign.py --delay-seconds` |
| **自訂 SMTP 伺服器** | 若不用 Mailgun，可在 `EmailSender` 傳入 `smtp_server`、`smtp_port` |

### 4.2 模板與個人化

| 改動 | 說明 |
|------|------|
| **新增模板** | 在 `templates/minara/` 或 `templates/nftgo/` 新增 `.html` |
| **新增占位符** | 在 `personalize_template()` 中擴展：如 `{{company}}`、`{{link}}` 等 |
| **支援更多欄位** | 用戶 JSON 中增加 `username`、`company` 等，模板用 `{{field}}` 引用 |
| **本地預覽** | `python serve_templates.py` 在瀏覽器預覽模板 |

**目前支援的模板占位符：**
- `{{name}}`、`{User}`：顯示名稱（優先 `name` → `username` → email 前綴）
- `{{email}}`、`#{email}`：郵箱
- `#{verify_email_url}`：驗證連結（若有）
- `Hey there,` / `Hi there,`：會替換為 `Hey {name},` 等問候語

### 4.3 用戶數據

| 改動 | 說明 |
|------|------|
| **txt → json** | `python src/convert_txt_to_json.py data/minara/users.txt` |
| **csv → json** | `python src/convert_csv_to_json.py <input.csv>` |
| **excel → json** | `python src/convert_excel_to_json.py <input.xlsx>` |
| **用戶結構** | 每筆至少需 `email`；`name`、`username` 用於個人化顯示 |

**JSON 示例：**
```json
[
  {"id": 1, "email": "user@example.com", "name": "John"},
  {"id": 2, "email": "other@example.com", "name": ""}
]
```

### 4.4 發送邏輯與腳本

| 改動 | 說明 |
|------|------|
| **跳過退訂過濾** | `send_bulk_emails(..., skip_unsubscribe_check=True)` |
| **新增 campaign 腳本** | 仿照 `minara_campaign.py`，載入對應 config 與路徑 |
| **改用 SMTP** | 在 campaign 中改 `method='smtp'` |
| **批次大小與間隔** | `batch_campaign.py --batch-size 600 --delay-hours 20` |

### 4.5 退訂管理

| 改動 | 說明 |
|------|------|
| **查看退訂列表** | `python src/unsubscribe_manager.py` |
| **過濾邏輯** | 修改 `UnsubscribeManager.filter_user_list()` |
| **支援標籤過濾** | 目前 `get_all_unsubscribes()` 不支援 tag 過濾，可擴展呼叫 Mailgun 分 tag 查詢 |

### 4.6 日誌與進度

| 改動 | 說明 |
|------|------|
| **日誌路徑** | `setup_logging('campaigns/minara/email_send.log')` 可改為其他路徑 |
| **進度檔路徑** | `batch_campaign.py` 中 `PROGRESS_DIR`，預設 `campaigns/minara/progress/` |
| **進度檔命名** | 依用戶檔名自動生成，如 `biglist-progress.json` |

### 4.7 程式碼層面擴展

| 改動 | 說明 |
|------|------|
| **支援純文字正文** | `send_via_mailgun_api` 已有 `text` 參數，可在模板中產出 plain text |
| **附件** | 目前無附件支援，需擴展 API 或 SMTP 的 `multipart` 處理 |
| **排程** | 可搭配 cron 或 systemd timer 定時執行 `batch_campaign.py` |
| **錯誤重試** | 目前無重試，可在 `send_via_mailgun_api` / `send_via_smtp` 中加 retry 邏輯 |

---

## 五、常用命令速查

```bash
# 1. 配置
cp config.example.py config.py
# 編輯 config.py 填入 Mailgun 憑證

# 2. txt 轉 json
python src/convert_txt_to_json.py data/minara/users.txt

# 3. 發測試信（API）
python campaigns/minara_campaign.py --test your@email.com \
  --template sharpe-guard-v2-launch.html \
  --subject "Test Subject" --tags test

# 4. 正式單次發送
python campaigns/minara_campaign.py \
  --template sharpe-guard-v2-launch.html \
  --users 03-07-autopilot-non-active-user.json \
  --subject "Your subject" --tags sharpe-guard-v2

# 5. 大列表分批發送（可斷點續傳）
python campaigns/batch_campaign.py \
  --users data/minara/biglist.json \
  --template templates/minara/sharpe-guard-v2-launch.html \
  --subject "Your subject" \
  --batch-size 600 --delay-hours 20

# 6.  dry-run（不實際發送）
python campaigns/minara_campaign.py --dry-run ...

# 7. 本地預覽模板
python serve_templates.py
# 開啟 http://localhost:8000/xxx.html
```

---

## 六、注意事項

1. **config.py** 在 `.gitignore` 中，不會被提交，請自行備份憑證。
2. **NFTGo** 使用 `NFTGO_CONFIG`，需在 `config.py` 中自行新增該配置塊。
3. **batch_campaign** 僅使用 Mailgun API，不支援 SMTP 模式。
4. 大規模發送時建議用 **tmux** 或 **screen** 保持會話，避免 SSH 斷線中斷任務。
5. 發送前會自動過濾 Mailgun 退訂列表（API 模式），確保符合 CAN-SPAM 等規範。
