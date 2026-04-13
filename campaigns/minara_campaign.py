#!/usr/bin/env python3
"""
Minara Email Campaign Script
Usage: python campaigns/minara_campaign.py [--dry-run] [--test <email>] [--subject <text>]
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_sender import EmailSender, load_users_from_json, setup_logging
from config import MINARA_CONFIG

def main():
    parser = argparse.ArgumentParser(description='Run Minara email campaign')
    parser.add_argument('--dry-run', action='store_true', help='Test mode - no emails sent')
    parser.add_argument('--test', type=str, help='Send test email to specified address')
    parser.add_argument('--template', default='3-event-user-reactivation.html',
                       help='Template filename (in templates/minara/)')
    parser.add_argument('--users', default='ai-meet-digital-finance.json',
                       help='User data filename (in data/minara/)')
    parser.add_argument('--subject', type=str, default='Getting started with Minara',
                       help='Email subject line')
    parser.add_argument('--tags', nargs='+', default=None,
                       help='Mailgun tracking tags (e.g. --tags sharpe-guard-v2 autopilot)')
    parser.add_argument('--yes', action='store_true',
                       help='Skip confirmation prompt when sending to real users (non-interactive)')
    args = parser.parse_args()

    # Default tags if not provided
    template_slug = args.template.replace('.html', '')
    tags = args.tags if args.tags else ['minara', template_slug]

    # Setup logging
    setup_logging('campaigns/minara/email_send.log')

    # Initialize sender
    sender = EmailSender(**MINARA_CONFIG)

    # Test mode
    if args.test:
        print(f"🧪 Sending test email to {args.test}")
        sender.send_test_email(
            template_path=f'templates/minara/{args.template}',
            test_email=args.test,
            subject=args.subject,
            method='api',
            tags=['test'] + tags
        )
        return

    # Load users
    print("📂 Loading users...")
    users = load_users_from_json(f'data/minara/{args.users}')

    if not users:
        print("❌ No users found")
        return

    print(f"✅ Loaded {len(users)} users")

    template_path = f'templates/minara/{args.template}'

    print(f"\n📧 Email Campaign:")
    print(f"   Template: {template_path}")
    print(f"   Subject:  {args.subject}")
    print(f"   Tags:     {tags}")
    print(f"   Recipients: {len(users)}")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'PRODUCTION'}")

    if not args.dry_run and not args.yes:
        confirm = input("\n⚠️  Send emails to real users? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Campaign cancelled")
            return

    sender.send_bulk_emails(
        template_path=template_path,
        users_data=users,
        subject=args.subject,
        method='api',
        dry_run=args.dry_run,
        tags=tags
    )

if __name__ == '__main__':
    main()
