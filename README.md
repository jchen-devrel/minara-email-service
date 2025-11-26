# Email Service with Mailgun

Send personalized bulk emails via Mailgun SMTP. Same email sending logic as before, now better organized and easier to use.

## 📁 Structure

```
minara-email-service/
├── src/
│   └── email_sender.py          # Core email sender (unified from old code)
├── campaigns/
│   ├── minara_campaign.py       # Minara emails
│   └── nftgo_campaign.py        # NFTGo emails
├── templates/
│   ├── minara/*.html            # Minara email templates
│   └── nftgo/*.html             # NFTGo email templates
├── data/
│   ├── minara/*.json            # Minara user lists
│   └── nftgo/*.json             # NFTGo user lists
└── config.py                    # Your credentials (gitignored)
```

## 🚀 Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Your config is ready
Credentials are already in `config.py` (this file is gitignored for security).

### 3. Send test email
```bash
python campaigns/minara_campaign.py --test your@email.com
python campaigns/nftgo_campaign.py --test your@email.com
```

### 4. Preview campaign (no emails sent)
```bash
python campaigns/minara_campaign.py --dry-run
python campaigns/nftgo_campaign.py --dry-run
```

### 5. Send for real
```bash
python campaigns/minara_campaign.py
python campaigns/nftgo_campaign.py
```

## 📧 Your Workflow (Unchanged!)

**Same as before:**

```
Excel/CSV → convert to JSON → send emails
```

**Important:** Put your files in `data/minara/` or `data/nftgo/` so campaigns can find them.

### Convert data files:

```bash
# Excel to JSON
python src/convert_excel_to_json.py data/nftgo/input.xlsx data/nftgo/output.json

# CSV to JSON  
python src/convert_csv_to_json.py data/minara/input.csv data/minara/output.json

# Then use the JSON file
python campaigns/nftgo_campaign.py --users output.json
```

### JSON format (same as before):
```json
[
  {
    "email": "user@example.com",
    "name": "John Doe",
    "username": "johndoe"
  }
]
```

## 🎯 Choosing Which Data File to Use

### Your current data files:

**Minara** (`data/minara/`):
- `extracted_users.json` (default)
- `extracted_users copy.json`
- `xneuro.users.json`

**NFTGo** (`data/nftgo/`):
- `nftgo_users.json` (default, ~3,190 users)
- `nftgo_b_users.json` (~19,802 users!)
- `extracted_users.json` (small test list)

### Use command-line arguments:

```bash
# Use different user file
python campaigns/minara_campaign.py --users xneuro.users.json --dry-run
python campaigns/nftgo_campaign.py --users nftgo_b_users.json --dry-run

# Use different template
python campaigns/minara_campaign.py --template credits-20-percent.html --dry-run
python campaigns/nftgo_campaign.py --template introduce-minara-to-c.html --dry-run

# Combine both
python campaigns/nftgo_campaign.py \
  --template introduce-minara-to-b.html \
  --users nftgo_b_users.json \
  --dry-run
```

### Or edit the default in the script:

**campaigns/minara_campaign.py** line 24:
```python
parser.add_argument('--users', default='extracted_users.json',  # Change this
```

**campaigns/nftgo_campaign.py** line 24:
```python
parser.add_argument('--users', default='nftgo_users.json',  # Change this
```

## 📝 Email Templates

Templates are in `templates/campaign/` and use the same personalization as before:

- `{{name}}` - User's name
- `{{email}}` - User's email
- `Hey there,` → Auto-converts to `Hey John,`

**Name priority:** `name` field → `username` field → email prefix

## ⚙️ What Changed from Old Code?

### What's the SAME:
✅ Email sending logic identical (SMTP, Mailgun, personalization)  
✅ Same credentials  
✅ Same workflow (Excel/CSV → JSON → send)  
✅ Same template system  
✅ Same rate limiting  

### What's BETTER:
✅ One unified `email_sender.py` instead of duplicates  
✅ Organized directory structure  
✅ Choose data files via command line  
✅ Better logging  
✅ Test mode (`--test`) and dry-run (`--dry-run`)  
✅ Confirmation before sending to avoid mistakes  

## 🔧 Common Commands

```bash
# Send test email
python campaigns/minara_campaign.py --test your@email.com

# Preview (no emails sent)
python campaigns/minara_campaign.py --dry-run

# Use different data file
python campaigns/minara_campaign.py --users xneuro.users.json --dry-run

# Use different template
python campaigns/minara_campaign.py --template credits-20-percent.html --dry-run

# Send production emails
python campaigns/minara_campaign.py

# NFTGo with big user list
python campaigns/nftgo_campaign.py --users nftgo_b_users.json

# Check logs
tail -f campaigns/minara/email_send.log
tail -f campaigns/nftgo/email_send.log
```

## 📊 Available Options

All campaigns support:

| Flag | Description | Example |
|------|-------------|---------|
| `--test EMAIL` | Send test email | `--test you@email.com` |
| `--dry-run` | Preview without sending | `--dry-run` |
| `--users FILE` | Choose data file | `--users nftgo_b_users.json` |
| `--template FILE` | Choose template | `--template feedback.html` |

## 🔐 Security

- ✅ `config.py` - Credentials protected (gitignored)
- ✅ `data/*.json` - User data private (gitignored)
- ✅ `*.log` - Logs not committed (gitignored)

## 📈 Best Practices

1. **Always test first:**
   ```bash
   python campaigns/campaign.py --test your@email.com
   ```

2. **Then dry-run:**
   ```bash
   python campaigns/campaign.py --dry-run
   ```

3. **Check user count:**
   ```bash
   python -c "import json; print(len(json.load(open('data/nftgo/nftgo_users.json'))))"
   ```

4. **For large lists (19K+ users), send in batches**

5. **Monitor logs during sending:**
   ```bash
   tail -f campaigns/*/email_send.log
   ```

## 🛠️ Troubleshooting

**"No users found"**
```bash
# Check if file exists
ls data/minara/

# Try different file
python campaigns/minara_campaign.py --users "extracted_users copy.json"
```

**Empty data file**
```bash
# Convert from CSV/Excel (files in data/ directory)
python src/convert_csv_to_json.py data/minara/file.csv data/minara/file.json
```

**Emails not sending**
- Check credentials in `config.py`
- Verify Mailgun domain is active
- Check logs: `tail campaigns/*/email_send.log`

## 💡 Examples

### Scenario 1: New Excel file
```bash
# Put file in data/nftgo/new_leads.xlsx, then:

# Convert
python src/convert_excel_to_json.py data/nftgo/new_leads.xlsx data/nftgo/new_leads.json

# Test
python campaigns/nftgo_campaign.py --users new_leads.json --test your@email.com

# Dry run
python campaigns/nftgo_campaign.py --users new_leads.json --dry-run

# Send
python campaigns/nftgo_campaign.py --users new_leads.json
```

### Scenario 2: Send different templates to different groups
```bash
# Template B to Group B
python campaigns/nftgo_campaign.py \
  --template introduce-minara-to-b.html \
  --users nftgo_b_users.json

# Template C to Group C
python campaigns/nftgo_campaign.py \
  --template introduce-minara-to-c.html \
  --users nftgo_c_users.json
```

### Scenario 3: Multiple campaigns same day
```bash
# Morning: Feedback campaign
python campaigns/minara_campaign.py \
  --template feedback-request.html \
  --users extracted_users.json

# Afternoon: Credits campaign  
python campaigns/minara_campaign.py \
  --template credits-20-percent.html \
  --users xneuro.users.json
```

## 📦 Using EmailSender Directly

For custom campaigns:

```python
from src.email_sender import EmailSender, load_users_from_json, setup_logging
from config import MINARA_CONFIG

# Setup
setup_logging('my_campaign.log')
sender = EmailSender(**MINARA_CONFIG)

# Load users
users = load_users_from_json('data/users.json')

# Send
sender.send_bulk_emails(
    template_path='templates/my_template.html',
    users_data=users,
    subject='Email Subject',
    method='smtp',
    dry_run=False
)
```

## 🔄 Rate Limiting

Adjust in `config.py`:

```python
MINARA_CONFIG = {
    'delay_between_emails': 1,   # Fast: 1/sec
}

NFTGO_CONFIG = {
    'delay_between_emails': 20,  # Slow: 1 per 20 sec (safer)
}
```

## ✅ Summary

**What you need to know:**
1. Same email sending as before, just better organized
2. Use `--users FILENAME.json` to choose which data file
3. Always test with `--test` and `--dry-run` first
4. Your workflow: Excel/CSV → convert to JSON → send
5. One README, everything you need is here

**Quick commands:**
```bash
# Test
python campaigns/minara_campaign.py --test your@email.com

# Preview  
python campaigns/minara_campaign.py --dry-run

# Send
python campaigns/minara_campaign.py
```

**Common commands**:

```bash
python3 campaigns/minara_campaign.py --users test-list.json --template 11-26-pre-launch-update.html --subject "Minara Is Now Open to Everyone"

python3 campaigns/nftgo_campaign.py --users nftgo_users.json --template introduce-minara-to-b.html

python3 src/convert_txt_to_json.py data/minara/11-26-heavy-and-active-user.txt data/minara/11-26-heavy-and-active-user.json --source "heavy-and-active"
```


---

Need help? Check logs in `campaigns/*/email_send.log`
