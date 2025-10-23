#!/usr/bin/env python3
"""
Convert email list from txt file to JSON format for email campaigns
Usage: python src/convert_emails_to_json.py
"""

import json
from pathlib import Path

def convert_emails_to_json():
    """Convert email list from txt to JSON format"""
    
    # Read emails from txt file
    txt_file = Path('ai-meet-digital-finance.txt')
    json_file = Path('data/minara/ai-meet-digital-finance.json')
    
    if not txt_file.exists():
        print(f"❌ File not found: {txt_file}")
        return
    
    print(f"📂 Reading emails from {txt_file}")
    
    # Read and clean emails
    emails = []
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            email = line.strip()
            if email and '@' in email:  # Basic email validation
                emails.append(email)
    
    print(f"✅ Found {len(emails)} valid emails")
    
    # Remove duplicates while preserving order
    unique_emails = list(dict.fromkeys(emails))
    print(f"📊 After removing duplicates: {len(unique_emails)} emails")
    
    # Convert to JSON format (matching existing structure)
    users_data = []
    for i, email in enumerate(unique_emails, 1):
        user_data = {
            "id": i,
            "email": email,
            "name": "",  # Empty name field
            "source": "ai-meet-digital-finance-event"
        }
        users_data.append(user_data)
    
    # Ensure directory exists
    json_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Converted to JSON: {json_file}")
    print(f"📧 Ready to use with email campaigns!")
    
    # Show sample of converted data
    print(f"\n📋 Sample data:")
    for user in users_data[:3]:
        print(f"   {user['email']}")

if __name__ == '__main__':
    convert_emails_to_json()
