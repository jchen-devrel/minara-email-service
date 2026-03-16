"""
Configuration template — copy this to config.py and fill in your credentials.
config.py is gitignored and will never be committed.
"""

# Minara Campaign Configuration
MINARA_CONFIG = {
    'smtp_username': 'your-smtp-username@minara.ai',     # Mailgun SMTP username
    'smtp_password': 'your-mailgun-smtp-password',        # Mailgun SMTP password
    'from_email': 'koda@minara.ai',                       # Sender email address
    'from_name': 'Koda from Minara',                      # Sender display name
    'delay_between_emails': 20,                           # Seconds between emails (20 = safe)

    # Mailgun API (used for tracking & unsubscribe features)
    'mailgun_domain': 'minara.ai',                        # Your Mailgun sending domain
    'mailgun_api_key': 'your-mailgun-api-key',            # Mailgun API key (Private API Key)
}
