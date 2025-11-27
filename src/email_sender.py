#!/usr/bin/env python3
"""
Unified Email Sender - Supports both SMTP and Mailgun API
Works with multiple email campaigns and personalization
"""

import smtplib
import json
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
import time
import sys
from pathlib import Path

# Optional import for Mailgun API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Configure logging
def setup_logging(log_file='email_send.log'):
    """Configure logging for email sending"""
    # Create directory for log file if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

class EmailSender:
    """
    Unified email sender class supporting both SMTP and Mailgun API
    
    Usage:
        sender = EmailSender(
            smtp_username="your@email.com",
            smtp_password="your-password",
            from_email="your@email.com",
            from_name="Your Name"
        )
    """
    
    def __init__(self, smtp_username, smtp_password, from_email, from_name, 
                 smtp_server="smtp.mailgun.org", smtp_port=587,
                 mailgun_domain=None, mailgun_api_key=None,
                 delay_between_emails=1):
        """
        Initialize email sender with credentials
        
        Args:
            smtp_username: SMTP username (usually email address)
            smtp_password: SMTP password/API key
            from_email: Sender email address
            from_name: Sender display name
            smtp_server: SMTP server address (default: Mailgun)
            smtp_port: SMTP port (default: 587)
            mailgun_domain: Mailgun domain (optional, for API method)
            mailgun_api_key: Mailgun API key (optional, for API method)
            delay_between_emails: Seconds to wait between emails (rate limiting)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name
        self.mailgun_domain = mailgun_domain
        self.mailgun_api_key = mailgun_api_key
        self.delay_between_emails = delay_between_emails
        
    def load_template(self, template_path):
        """Load HTML email template from file"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Failed to load template {template_path}: {e}")
            return None
    
    def personalize_template(self, template, user_data):
        """
        Replace placeholders in template with user data
        
        Supports placeholders:
            {{name}}, {User}, {{email}}, #{email}, #{verify_email_url}, etc.
        """
        personalized = template
        
        # Determine best display name: name > username > email prefix
        display_name = ""
        if 'name' in user_data and user_data['name']:
            display_name = user_data['name']
        elif 'username' in user_data and user_data['username']:
            display_name = user_data['username']
        elif 'email' in user_data:
            display_name = user_data['email'].split('@')[0]
        
        # Replace common placeholders
        if display_name:
            personalized = personalized.replace('{{name}}', display_name)
            personalized = personalized.replace('{User}', display_name)
            personalized = personalized.replace('Hey there,', f"Hey {display_name},")
            personalized = personalized.replace('Hi there,', f"Hi {display_name},")
        
        if 'email' in user_data:
            personalized = personalized.replace('{{email}}', user_data['email'])
            personalized = personalized.replace('#{email}', user_data['email'])
        
        # Additional custom placeholders
        if 'verify_email_url' in user_data:
            personalized = personalized.replace('#{verify_email_url}', user_data['verify_email_url'])
        
        return personalized
    
    def send_via_smtp(self, to_email, to_name, subject, html_content, plain_content=None):
        """Send email via SMTP (recommended for most use cases)"""
        try:
            # Replace placeholder in HTML content
            personalized_html = html_content.replace('%recipient_email%', to_email)
            
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = f"{to_name} <{to_email}>" if to_name else to_email
            msg['Subject'] = subject
            
            if plain_content:
                part1 = MIMEText(plain_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(personalized_html, 'html')
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logging.info(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to send to {to_email}: {e}")
            return False
    
    def send_via_mailgun_api(self, to_email, to_name, subject, html_content, plain_content=None, tags=None):
        """Send email via Mailgun API (alternative method)"""
        if not REQUESTS_AVAILABLE:
            logging.error("requests library not available")
            return False
            
        if not self.mailgun_domain or not self.mailgun_api_key:
            logging.error("Mailgun API credentials not configured")
            return False
            
        try:
            url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages"
            
            # Replace placeholder in HTML content
            personalized_html = html_content.replace('%recipient_email%', to_email)
            
            data = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": f"{to_name} <{to_email}>" if to_name else to_email,
                "subject": subject,
                "html": personalized_html,
                
                # ✅ Enable tracking
                "o:tracking": "yes",
                "o:tracking-opens": "yes",
                "o:tracking-clicks": "yes",
                
                # ✅ Security
                "o:require-tls": "yes",
                
                # ✅ Automatic unsubscribe - Mailgun will handle everything
                "o:tracking-unsubscribe": "yes",
                
                # ✅ Unsubscribe headers (RFC 2369 & RFC 8058)
                "h:List-Unsubscribe": f"<%unsubscribe_url%>",
                "h:List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                
                # ✅ List identification
                "h:List-Id": f"Minara Updates <updates.{self.mailgun_domain}>",
                "h:Precedence": "bulk",
            }
            
            if plain_content:
                data["text"] = plain_content
            
            # Add tags if provided
            if tags:
                for tag in tags:
                    data[f"o:tag"] = tag
            
            response = requests.post(
                url,
                auth=("api", self.mailgun_api_key),
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                logging.info(f"✅ Email sent to {to_email} via API")
                return True
            else:
                logging.error(f"❌ API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Failed to send to {to_email} via API: {e}")
            return False
    
    def send_test_email(self, template_path, test_email, subject, user_data=None, method="smtp", tags=None):
        """
        Send a test email
        
        Args:
            template_path: Path to HTML template
            test_email: Recipient email for testing
            subject: Email subject line
            user_data: Optional user data for personalization
            method: 'smtp' or 'api'
            tags: Optional list of tags for Mailgun (only used with API method)
        """
        logging.info(f"🧪 Sending test email to {test_email}")
        
        template = self.load_template(template_path)
        if not template:
            return False
        
        # Use provided user data or create sample
        if not user_data:
            user_data = {
                'email': test_email,
                'name': test_email.split('@')[0]
            }
        
        html_content = self.personalize_template(template, user_data)
        
        display_name = user_data.get('name', '') or user_data.get('username', '') or test_email.split('@')[0]
        
        if method == "smtp":
            return self.send_via_smtp(test_email, display_name, subject, html_content)
        else:
            return self.send_via_mailgun_api(test_email, display_name, subject, html_content, tags=tags)
    
    def send_bulk_emails(self, template_path, users_data, subject, method="smtp", dry_run=False, tags=None, skip_unsubscribe_check=False):
        """
        Send emails to multiple users
        
        Args:
            template_path: Path to HTML template
            users_data: List of user dictionaries with 'email' and other fields
            subject: Email subject line
            method: 'smtp' or 'api'
            dry_run: If True, only simulate sending (for testing)
            tags: Optional list of tags for Mailgun (only used with API method)
            skip_unsubscribe_check: If True, skip checking Mailgun suppression list
        """
        if dry_run:
            logging.info("🔍 DRY RUN MODE - No emails will be sent")
        
        # Filter out unsubscribed users (only if using API method)
        if method == "api" and not skip_unsubscribe_check and self.mailgun_domain and self.mailgun_api_key:
            try:
                from .unsubscribe_manager import UnsubscribeManager
                manager = UnsubscribeManager(self.mailgun_domain, self.mailgun_api_key)
                original_count = len(users_data)
                users_data = manager.filter_user_list(users_data)
                filtered_count = original_count - len(users_data)
                if filtered_count > 0:
                    logging.info(f"🚫 Filtered out {filtered_count} unsubscribed users")
            except Exception as e:
                logging.warning(f"⚠️  Could not check unsubscribe list: {e}")
        
        template = self.load_template(template_path)
        if not template:
            logging.error("❌ Failed to load template")
            return
        
        total = len(users_data)
        success = 0
        failed = 0
        
        logging.info(f"📧 Starting bulk send to {total} users")
        
        for i, user in enumerate(users_data, 1):
            try:
                email = user.get('email', '').strip()
                
                if not email:
                    logging.warning(f"⚠️  Skipping user {i}: No email")
                    failed += 1
                    continue
                
                display_name = user.get('name', '') or user.get('username', '') or email.split('@')[0]
                html_content = self.personalize_template(template, user)
                
                if dry_run:
                    logging.info(f"📝 Would send to: {display_name} <{email}> ({i}/{total})")
                    success += 1
                else:
                    if method == "smtp":
                        result = self.send_via_smtp(email, display_name, subject, html_content)
                    else:
                        result = self.send_via_mailgun_api(email, display_name, subject, html_content, tags=tags)
                    
                    if result:
                        success += 1
                    else:
                        failed += 1
                    
                    if i < total:
                        time.sleep(self.delay_between_emails)
                
                if i % 10 == 0 or i == total:
                    logging.info(f"📊 Progress: {i}/{total}")
                    
            except Exception as e:
                logging.error(f"❌ Error processing user {i}: {e}")
                failed += 1
        
        # Summary
        logging.info(f"📋 Campaign completed!")
        logging.info(f"✅ Successful: {success}")
        logging.info(f"❌ Failed: {failed}")
        logging.info(f"📊 Success rate: {success/total*100:.1f}%")


def load_users_from_csv(csv_path):
    """Load users from CSV file"""
    users = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(row)
        logging.info(f"📂 Loaded {len(users)} users from {csv_path}")
        return users
    except Exception as e:
        logging.error(f"❌ Failed to load CSV: {e}")
        return []


def load_users_from_json(json_path):
    """Load users from JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
        logging.info(f"📂 Loaded {len(users)} users from {json_path}")
        return users
    except Exception as e:
        logging.error(f"❌ Failed to load JSON: {e}")
        return []

