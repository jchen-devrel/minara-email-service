# minara-email-service

Mailgun API 發送個人化批量郵件。

## 設定

```bash
cp config.example.py config.py
```

然後編輯 `config.py`，填入你的 Mailgun 憑證：

```python
MINARA_CONFIG = {
    'smtp_username': 'your-smtp-username@minara.ai',
    'smtp_password': 'your-mailgun-smtp-password',
    'from_email': 'koda@minara.ai',
    'from_name': 'Koda from Minara',
    'delay_between_emails': 20,
    'mailgun_domain': 'minara.ai',
    'mailgun_api_key': 'your-mailgun-api-key',  # Mailgun → Settings → API Keys → Private API Key
}
```

> `config.py` 已在 `.gitignore`，不會被 commit。

## 結構

```
campaigns/minara_campaign.py   # 主發送腳本
templates/minara/*.html        # 郵件模板
data/minara/*.json             # 用戶列表
config.py                      # 憑證（gitignored）
```

## 常用指令

```bash
# txt 轉 json（自動同名輸出）
python src/convert_txt_to_json.py data/minara/users.txt

# 發測試信
python campaigns/minara_campaign.py \
  --test frank@minara.ai \
  --template sharpe-guard-v2-launch.html \
  --subject "Your subject here"

# 正式發送
python campaigns/minara_campaign.py \
  --template sharpe-guard-v2-launch.html \
  --users 03-07-autopilot-non-active-user.json \
  --subject "Your subject here"

# 查看進度
tail -f campaigns/minara/email_send.log
```

## 參數說明

| 參數 | 說明 |
|------|------|
| `--test EMAIL` | 只發一封測試信 |
| `--template FILE` | 模板檔名（在 templates/minara/ 下） |
| `--users FILE` | 用戶 JSON 檔名（在 data/minara/ 下） |
| `--subject TEXT` | 郵件標題 |
| `--dry-run` | 模擬發送，不實際送出 |

## 大列表自動分批發送

```bash
python campaigns/batch_campaign.py \
  --users data/minara/biglist.json \
  --template templates/minara/my-template.html \
  --subject "Your subject" \
  --batch-size 1500 \
  --delay-hours 24
```

- 自動切成每天 1500 封，發完一批等 24 小時再發下一批
- 每封發完就存進度，VM 重啟後重新跑同一指令會**自動從斷點繼續**，不會重複發
- 進度檔存在 `campaigns/minara/progress/`

## 速率設定

`config.py` 裡 `delay_between_emails: 20`（秒），453 封約 2.5 小時，對 Mailgun 和 domain 安全。



### 通过后台建立tmux自动跑脚本（detached模式）
```bash
tmux new-session -d -s email-campaign "python campaigns/batch_campaign.py ..."
```