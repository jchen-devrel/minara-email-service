#!/usr/bin/env python3
"""
Extract username and email from CSV file and save to JSON
"""

import csv
import json
import sys
import re
from pathlib ixmport Path

def clean_name(name):
    """Clean problematic characters from name"""
    if not name:
        return ""
    
    # Remove invisible Unicode characters and control characters
    name = re.sub(r'[\u200b-\u200f\u202a-\u202e\u2060-\u206f]', '', name)
    # Remove other problematic characters but keep basic punctuation
    name = re.sub(r'[^\w\s\-\.\,\'\"]', '', name)
    # Clean up extra spaces
    name = ' '.join(name.split())
    
    return name.strip()

def extract_users_from_csv(csv_file, output_file=None):
    """Extract username and email from CSV file"""
    users = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                
                # Skip rows without email
                if not email:
                    continue
                
                user_data = {
                    'username': username,
                    'email': email
                }
                
                # Add name - prefer displayName, fallback to username
                display_name = row.get('displayName', '').strip()
                if display_name and display_name != email:
                    cleaned_name = clean_name(display_name)
                    user_data['name'] = cleaned_name if cleaned_name else username
                else:
                    user_data['name'] = username
                
                users.append(user_data)
        
        print(f"✅ Extracted {len(users)} users from {csv_file}")
        
        # Save to JSON file
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved to {output_file}")
        
        return users
        
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return []

def main():
    """Main function"""
    csv_file = "74429_2025_09_17.csv"
    output_file = "extracted_users.json"
    
    print("🔄 Extracting users from CSV...")
    print("=" * 50)
    
    # Extract users
    users = extract_users_from_csv(csv_file, output_file)
    
    if users:
        print(f"\n📊 Summary:")
        print(f"   Total users: {len(users)}")
        print(f"   First few users:")
        
        # Show first 5 users as preview
        for i, user in enumerate(users[:5], 1):
            name_info = f" ({user.get('name', 'No name')})" if 'name' in user else ""
            print(f"   {i}. {user['username']} - {user['email']}{name_info}")
        
        if len(users) > 5:
            print(f"   ... and {len(users) - 5} more users")
    
    print(f"\n✅ Done! Check {output_file}")

if __name__ == "__main__":
    main()
