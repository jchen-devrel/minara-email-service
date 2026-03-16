#!/usr/bin/env python3
"""
Batch Email Campaign - Auto-sends in daily batches with resume support.

Usage:
  python campaigns/batch_campaign.py \
    --users data/minara/biglist.json \
    --template templates/minara/my-template.html \
    --subject "Your subject" \
    --batch-size 1500 \
    --delay-hours 24

Features:
  - Splits user list into daily batches automatically
  - Sleeps between batches (default 24 hours)
  - Saves progress → safe to resume after VM restart
  - Won't re-send to already-sent emails
"""

import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_sender import EmailSender, setup_logging
from config import MINARA_CONFIG

PROGRESS_DIR = Path("campaigns/minara/progress")


def load_progress(progress_file):
    if progress_file.exists():
        with open(progress_file) as f:
            return json.load(f)
    return {"sent_emails": [], "current_batch": 0}


def save_progress(progress_file, sent_emails, current_batch):
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    with open(progress_file, "w") as f:
        json.dump({"sent_emails": sent_emails, "current_batch": current_batch}, f, indent=2)


def sleep_until_next_batch(hours):
    resume_at = datetime.now() + timedelta(hours=hours)
    logging.info(f"⏳ Batch done. Next batch at {resume_at.strftime('%Y-%m-%d %H:%M')} (in {hours}h)")
    logging.info("   (Safe to detach tmux. Resume with: tmux attach -t email-campaign)")
    time.sleep(hours * 3600)


def main():
    parser = argparse.ArgumentParser(description="Auto batch email campaign with resume support")
    parser.add_argument("--users", required=True, help="Path to user JSON file")
    parser.add_argument("--template", required=True, help="Path to HTML template")
    parser.add_argument("--subject", required=True, help="Email subject line")
    parser.add_argument("--batch-size", type=int, default=1500, help="Emails per batch (default: 1500)")
    parser.add_argument("--delay-hours", type=float, default=24, help="Hours between batches (default: 24)")
    parser.add_argument("--delay-seconds", type=int, default=None, help="Override delay between individual emails (default: from config)")
    parser.add_argument("--tags", nargs="+", default=["batch-campaign"], help="Mailgun tags (default: batch-campaign)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without sending")
    args = parser.parse_args()

    setup_logging("campaigns/minara/email_send.log")

    # Load users
    with open(args.users) as f:
        all_users = json.load(f)
    total = len(all_users)

    # Progress file based on users filename
    users_stem = Path(args.users).stem
    progress_file = PROGRESS_DIR / f"{users_stem}-progress.json"

    # Load existing progress (resume support)
    progress = load_progress(progress_file)
    sent_set = set(progress["sent_emails"])
    start_batch = progress["current_batch"]

    if sent_set:
        logging.info(f"▶️  Resuming — {len(sent_set)}/{total} already sent")

    # Filter out already-sent users
    remaining = [u for u in all_users if u.get("email") not in sent_set]

    if not remaining:
        logging.info("✅ All emails already sent. Nothing to do.")
        return

    # Split remaining into batches
    batches = [remaining[i:i + args.batch_size] for i in range(0, len(remaining), args.batch_size)]
    total_batches = len(batches)

    logging.info(f"📋 Total users: {total} | Remaining: {len(remaining)} | Batches: {total_batches} × {args.batch_size}")
    logging.info(f"⏱  Delay between batches: {args.delay_hours}h | Estimated finish: {(datetime.now() + timedelta(hours=args.delay_hours * (total_batches - 1))).strftime('%Y-%m-%d %H:%M')}")

    if not args.dry_run:
        confirm = input("\n⚠️  Start batch campaign? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Cancelled")
            return

    # Init sender
    config = dict(MINARA_CONFIG)
    if args.delay_seconds is not None:
        config["delay_between_emails"] = args.delay_seconds
    sender = EmailSender(**config)

    for batch_idx, batch in enumerate(batches):
        batch_num = start_batch + batch_idx + 1
        logging.info(f"\n📦 Batch {batch_num}/{start_batch + total_batches} — {len(batch)} emails")

        for i, user in enumerate(batch, 1):
            email = user.get("email", "").strip()
            if not email:
                continue

            display_name = user.get("name", "") or user.get("username", "") or email.split("@")[0]

            template_content = sender.load_template(args.template)
            html = sender.personalize_template(template_content, user)

            if args.dry_run:
                logging.info(f"📝 [DRY RUN] Would send to: {email} ({i}/{len(batch)})")
            else:
                result = sender.send_via_mailgun_api(email, display_name, args.subject, html, tags=args.tags)
                if result:
                    sent_set.add(email)

                # Save progress after every email
                save_progress(progress_file, list(sent_set), batch_num)

                if i % 10 == 0 or i == len(batch):
                    logging.info(f"📊 Batch {batch_num} progress: {i}/{len(batch)}")

                if i < len(batch):
                    time.sleep(config.get("delay_between_emails", 20))

        logging.info(f"✅ Batch {batch_num} complete — Total sent: {len(sent_set)}/{total}")

        # Sleep before next batch (skip after last batch)
        if batch_idx < len(batches) - 1:
            sleep_until_next_batch(args.delay_hours)

    logging.info(f"\n🎉 All batches complete! Total sent: {len(sent_set)}/{total}")


if __name__ == "__main__":
    main()
