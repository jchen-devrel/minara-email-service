#!/usr/bin/env python3
"""
Convert an Excel recipient list to JSON and send a Minara campaign (Mailgun API).

Usage:
  python campaigns/send_from_excel.py path/to/recipients.xlsx \\
    --template strategy-studio-early-access.html \\
    --subject "Your subject" \\
    --tags campaign-name batch-1

  python campaigns/send_from_excel.py uploads/list.xlsx --dry-run ...
  python campaigns/send_from_excel.py uploads/list.xlsx --test you@minara.ai ...
  python campaigns/send_from_excel.py uploads/list.xlsx --yes ...   # skip confirm
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import MINARA_CONFIG
from src.convert_excel_to_json import convert_excel_to_json
from src.email_sender import EmailSender, load_users_from_json, setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Excel (.xlsx) to JSON and send Minara email campaign via Mailgun API."
    )
    parser.add_argument(
        "excel",
        type=str,
        help="Path to .xlsx (or .xls) file; must include an email column",
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Filename under templates/minara/ (e.g. strategy-studio-early-access.html)",
    )
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument(
        "--tags",
        nargs="+",
        default=None,
        help="Mailgun tags (default: minara + template slug)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Convert list and log what would be sent; no emails",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive confirmation for real sends (automation / agents)",
    )
    parser.add_argument(
        "--test",
        type=str,
        metavar="EMAIL",
        help="Send a single test to this address using the template, then exit",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Optional source string stored on each row in the generated JSON",
    )
    args = parser.parse_args()

    excel_path = Path(args.excel).expanduser().resolve()
    if not excel_path.is_file():
        print(f"❌ Excel not found: {excel_path}")
        sys.exit(1)
    if excel_path.suffix.lower() not in (".xlsx", ".xls"):
        print("❌ File must be .xlsx or .xls")
        sys.exit(1)

    data_dir = ROOT / "data" / "minara"
    data_dir.mkdir(parents=True, exist_ok=True)
    stem = excel_path.stem.replace(" ", "_")[:80]
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    json_path = data_dir / f"_excel_{stem}_{ts}.json"

    print(f"📥 Converting:\n   {excel_path}\n   → {json_path}")
    if not convert_excel_to_json(str(excel_path), str(json_path), args.source):
        sys.exit(1)

    setup_logging("campaigns/minara/email_send.log")
    users = load_users_from_json(str(json_path))
    if not users:
        print("❌ No valid recipients after conversion (need a column like email)")
        sys.exit(1)

    template_path = ROOT / "templates" / "minara" / args.template
    if not template_path.is_file():
        print(f"❌ Template not found: {template_path}")
        sys.exit(1)

    template_slug = args.template.replace(".html", "")
    tags = args.tags if args.tags else ["minara", template_slug]
    sender = EmailSender(**MINARA_CONFIG)

    if args.test:
        print(f"🧪 Sending test to {args.test}")
        ok = sender.send_test_email(
            template_path=str(template_path),
            test_email=args.test,
            subject=args.subject,
            method="api",
            tags=["test"] + tags,
        )
        sys.exit(0 if ok else 1)

    print(f"\n📧 Campaign")
    print(f"   Template:    {args.template}")
    print(f"   Recipients:  {len(users)}")
    print(f"   Subject:     {args.subject}")
    print(f"   Tags:        {tags}")
    print(f"   JSON:        {json_path.name}")
    print(f"   Mode:        {'DRY RUN' if args.dry_run else 'PRODUCTION'}")

    if not args.dry_run and not args.yes:
        confirm = input("\n⚠️  Send emails to real users? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Cancelled")
            sys.exit(1)

    sender.send_bulk_emails(
        template_path=str(template_path),
        users_data=users,
        subject=args.subject,
        method="api",
        dry_run=args.dry_run,
        tags=tags,
    )


if __name__ == "__main__":
    main()
