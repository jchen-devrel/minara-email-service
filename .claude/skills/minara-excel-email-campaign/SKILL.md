---
name: minara-excel-email-campaign
version: "1.0.0"
description: >-
  Send Minara bulk email campaigns from an Excel (.xlsx) recipient list via
  Mailgun API. Converts Excel to JSON, then sends using HTML templates in the
  minara-email-service repo. Use when the user uploads or mentions .xlsx
  recipients, Excel mailing list, bulk send from spreadsheet, or wants to send
  Minara email campaigns.
---

# Minara Excel → Email Campaign

Send Minara email campaigns from an Excel recipient list. Converts `.xlsx` → JSON → Mailgun API bulk send.

## When to Use

- User uploads or mentions a `.xlsx` / Excel recipient list
- User wants to send a Minara marketing / product email to a list
- User mentions "bulk email", "email campaign from spreadsheet", "send from Excel"

## Repository

All commands run from **repo root** (`minara-email-service/`).

## Prerequisites

1. **`config.py`** at repo root with valid `MINARA_CONFIG`:

```python
MINARA_CONFIG = {
    'smtp_username': '...',
    'smtp_password': '...',
    'from_email': 'hello@minara.ai',
    'from_name': 'Minara Team',
    'delay_between_emails': 20,
    'mailgun_domain': 'minara.ai',
    'mailgun_api_key': 'key-...',
}
```

If missing, tell user to `cp config.example.py config.py` and fill credentials. **Never invent keys.**

2. **Python deps**: `pip install -r requirements.txt` (needs `requests`, `pandas`, `openpyxl`).

3. **HTML template** under `templates/minara/`.

## Excel Format

- **Required column**: `email` / `Email` / `email_address` / `e-mail` / `account_id` (value must contain `@`).
- **Optional columns**: `name`, `full_name`, `username` — used for `{User}` / `{{name}}` personalization.
- First sheet is read. Save as `.xlsx`.

## One-Shot Command

```bash
python campaigns/send_from_excel.py "PATH/TO/recipients.xlsx" \
  --template TEMPLATE_FILE.html \
  --subject "Email subject line" \
  --tags tag1 tag2
```

### Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Convert + log what would be sent; no Mailgun calls |
| `--test EMAIL` | Send one test email, then exit |
| `--yes` | Skip interactive `yes/no` confirmation (automation/agents) |
| `--source NAME` | Optional; stored on each JSON row for traceability |

### Recommended Flow

```bash
# Step 1: dry run — verify list size and columns
python campaigns/send_from_excel.py uploads/list.xlsx \
  --template strategy-studio-early-access.html \
  --subject "Subject here" --dry-run

# Step 2: send one test to yourself
python campaigns/send_from_excel.py uploads/list.xlsx \
  --template strategy-studio-early-access.html \
  --subject "Subject here" --test you@minara.ai

# Step 3: real send (will prompt yes/no)
python campaigns/send_from_excel.py uploads/list.xlsx \
  --template strategy-studio-early-access.html \
  --subject "Subject here" --tags campaign batch-1
```

## Alternative (Two Steps)

```bash
# 1. Convert Excel → JSON
python src/convert_excel_to_json.py PATH/TO/file.xlsx data/minara/my-list.json

# 2. Send campaign
python campaigns/minara_campaign.py \
  --users my-list.json \
  --template strategy-studio-early-access.html \
  --subject "Subject" \
  --tags tag1 tag2
```

Add `--yes` to `minara_campaign.py` to skip confirmation.

## Available Templates

All under `templates/minara/`. Present this list when user needs to pick a template.

| Template file | Description | Best for |
|---------------|-------------|----------|
| `strategy-studio-early-access.html` | You now have access to Minara Strategy Studio (Early Access) | Early-access / feature unlock notification |
| `11-27-full-launch.html` | Today, Minara launches publicly | Major product launch, feature list + hero image |
| `sharpe-guard-v2-launch.html` | Sharpe Guard V2 is now live | Strategy/feature launch with multiple images |
| `discover-page-launch.html` | Explore Minara's new Discover page | Feature announcement with invite code |
| `referral-rewards-launch.html` | Invite friends. Earn Credits & Sparks. | Referral / rewards program launch |
| `credits-20-percent.html` | Your credits are running low | Credits low / upsell nudge |
| `invite-quota-refresh.html` | Invite quota refresh is available | Quota / credits refresh notification |
| `3-event-user-reactivation.html` | Getting started with Minara | Onboarding / reactivation for lapsed users |
| `11-12-user-feedback-request.html` | Can we chat about your Minara experience? | Feedback request, short & personal |
| `12-04-downgrade-user.html` | We'd love to hear from you | Downgrade / churn recovery feedback |
| `11-26-pre-launch-update.html` | Minara is now open to everyone | Pre-launch / early open announcement |
| `11-20-global-evangelist-meeting.html` | Minara is now open to everyone | Community / evangelist meeting invite |

### Choosing a template

- **Announcing a new feature / unlock**: `strategy-studio-early-access.html` or `discover-page-launch.html`
- **Big product launch**: `11-27-full-launch.html`
- **Strategy / Autopilot update**: `sharpe-guard-v2-launch.html`
- **Referral / rewards**: `referral-rewards-launch.html`
- **Credits / upsell**: `credits-20-percent.html`
- **User feedback**: `11-12-user-feedback-request.html` or `12-04-downgrade-user.html`
- **Onboarding / reactivation**: `3-event-user-reactivation.html`
- **General announcement**: `11-26-pre-launch-update.html`
- **None fit**: copy the closest template, rename, and edit the content inside.

### Template personalization

Templates use these placeholders (handled by `src/email_sender.py`):

| Placeholder | Replaced with |
|-------------|---------------|
| `{User}` | Display name (name → username → email prefix) |
| `{{name}}` | Same as above |
| `{{email}}` | Recipient email |
| `Hi there,` / `Hey there,` | Auto-changed to `Hi <name>,` / `Hey <name>,` |

## Agent Checklist

1. Confirm `config.py` exists at repo root.
2. Confirm Excel has an email column.
3. **Present the template table** and help user pick the right one.
4. Run `--dry-run` first unless user explicitly says to send.
5. Prefer `--test <user's email>` before full batch.
6. **Never** commit `config.py`, raw lists, or generated JSON — they are gitignored.
7. Logs: `campaigns/minara/email_send.log`.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `requests library not available` | `pip install requests` |
| Excel read errors | `pip install pandas openpyxl` |
| 0 recipients after conversion | Column names must match supported headers; values must contain `@` |
| `config.py` missing | `cp config.example.py config.py` and fill Mailgun fields |
