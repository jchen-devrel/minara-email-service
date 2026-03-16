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
    'from_email': 'xxx@minara.ai',
    'from_name': 'xxx from Minara',
    'delay_between_emails': 20,
    'mailgun_domain': 'minara.ai',
    'mailgun_api_key': 'your-mailgun-api-key',  # Mailgun → Settings → API Keys → Private API Key
}
```

> `config.py` 已在 `.gitignore`，不會被 commit。

## 結構

```
campaigns/minara_campaign.py   # 單次發送腳本
campaigns/batch_campaign.py    # 大列表分批發送腳本
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
  --subject "Your subject here" \
  --tags sharpe-guard-v2 test

# 正式發送
python campaigns/minara_campaign.py \
  --template sharpe-guard-v2-launch.html \
  --users 03-07-autopilot-non-active-user.json \
  --subject "Your subject here" \
  --tags sharpe-guard-v2 autopilot-non-active

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
| `--tags TAG1 TAG2` | Mailgun 追蹤標籤，可多個（不傳則自動用模板名稱） |
| `--dry-run` | 模擬發送，不實際送出 |

## 大列表自動分批發送

```bash
python campaigns/batch_campaign.py \
  --users data/minara/biglist.json \
  --template templates/minara/my-template.html \
  --subject "Your subject" \
  --tags sharpe-guard-v2 lapsed-user \
  --batch-size 600 \
  --delay-hours 20
```

- 自動切成每批 N 封，發完一批等 N 小時再發下一批
- 每封發完就存進度，VM 重啟後重新跑同一指令會**自動從斷點繼續**，不會重複發
- 進度檔存在 `campaigns/minara/progress/`

## 背景發送（斷開 SSH 不中斷）

```bash
tmux new -s email-campaign
# 跑指令，輸入 yes 確認後
# Ctrl+B 然後 D  →  detach，安全斷開 SSH

# 回來查看
tmux attach -t email-campaign
```

## 速率設定

`config.py` 裡 `delay_between_emails: 20`（秒），對 Mailgun 和 domain 安全。
