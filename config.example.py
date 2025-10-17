"""
Configuration file for email campaigns
Copy this file to config.py and fill in your credentials
"""

# Minara Campaign Configuration
MINARA_CONFIG = {
    'smtp_username': 'koda@minara.ai',
    'smtp_password': 'your-password-here',
    'from_email': 'koda@minara.ai',
    'from_name': 'Koda from Minara',
    'delay_between_emails': 1,  # seconds
}

# NFTGo Campaign Configuration
NFTGO_CONFIG = {
    'smtp_username': 'frank@nftgo.io',
    'smtp_password': 'your-password-here',
    'from_email': 'frank@nftgo.io',
    'from_name': 'Frank from NFTGo',
    'delay_between_emails': 20,  # seconds
}

# Alternative: Mailgun API Configuration (optional)
MAILGUN_API_CONFIG = {
    'mailgun_domain': 'mg.yourdomain.com',
    'mailgun_api_key': 'key-xxxxx',
}

# SMTP Server Configuration (Mailgun by default)
SMTP_CONFIG = {
    'smtp_server': 'smtp.mailgun.org',
    'smtp_port': 587,
}

