#!/usr/bin/env python3
"""
NFTGo Email Campaign Script
Usage: python campaigns/nftgo_campaign.py [--dry-run] [--test <email>] [--subject <text>]
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_sender import EmailSender, load_users_from_json, setup_logging
from config import NFTGO_CONFIG

def main():
    parser = argparse.ArgumentParser(description='Run NFTGo email campaign')
    parser.add_argument('--dry-run', action='store_true', help='Test mode - no emails sent')
    parser.add_argument('--test', type=str, help='Send test email to specified address')
    parser.add_argument('--template', default='introduce-minara-to-b.html', 
                       help='Template filename')
    parser.add_argument('--users', default='nftgo_users.json',
                       help='User data filename')
    parser.add_argument('--subject', type=str, default='NFTGo introduces Minara: your AI assistant for digital finance',
                       help='Email subject line')
    args = parser.parse_args()
    
    # Setup logging
    setup_logging('campaigns/nftgo/email_send.log')
    
    # Initialize sender
    sender = EmailSender(**NFTGO_CONFIG)
    
    # Test mode
    if args.test:
        print(f"🧪 Sending test email to {args.test}")
        sender.send_test_email(
            template_path=f'templates/nftgo/{args.template}',
            test_email=args.test,
            subject=args.subject,
            method='smtp'
        )
        return
    
    # Load users
    print("📂 Loading users...")
    users = load_users_from_json(f'data/nftgo/{args.users}')
    
    if not users:
        print("❌ No users found")
        return
    
    print(f"✅ Loaded {len(users)} users")
    
    # Campaign configuration
    template_path = f'templates/nftgo/{args.template}'
    subject = args.subject
    
    print(f"\n📧 Email Campaign:")
    print(f"   Template: {template_path}")
    print(f"   Subject: {subject}")
    print(f"   Recipients: {len(users)}")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'PRODUCTION'}")
    
    if not args.dry_run:
        confirm = input("\n⚠️  Send emails to real users? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Campaign cancelled")
            return
    
    # Send bulk emails
    sender.send_bulk_emails(
        template_path=template_path,
        users_data=users,
        subject=subject,
        method='smtp',
        dry_run=args.dry_run
    )

if __name__ == '__main__':
    main()

