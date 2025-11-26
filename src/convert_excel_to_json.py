#!/usr/bin/env python3
"""
Convert Excel file to JSON format for email campaigns
Usage: python src/convert_excel_to_json.py <input.xlsx> <output.json> [--source <source_name>]
"""

import pandas as pd
import json
import sys
import argparse
from pathlib import Path

def convert_excel_to_json(excel_file, json_file, source_name=None):
    """
    Convert Excel file to JSON format
    """
    try:
        # Read Excel file
        print(f"📂 Reading Excel file: {excel_file}")
        df = pd.read_excel(excel_file)

        # Display basic info about the data
        print(f"📊 Found {len(df)} rows and {len(df.columns)} columns")
        print(f"📋 Columns: {list(df.columns)}")

        # Show first few rows for verification
        print("\n🔍 First 3 rows:")
        print(df.head(3).to_string())

        # Convert DataFrame to list of dictionaries
        # Replace NaN values with None/empty strings as appropriate
        df = df.fillna('')  # Replace NaN with empty strings

        # Convert to list of dictionaries
        users_data = df.to_dict('records')

        # Clean up the data - ensure email field exists and is lowercase
        cleaned_data = []
        for user in users_data:
            # Convert all keys to lowercase for consistency
            cleaned_user = {}
            for key, value in user.items():
                # Common field name mappings
                if key.lower() in ['email', 'email_address', 'e-mail', 'account_id']:
                    # Check if the value looks like an email
                    email_value = str(value).strip().lower() if value else ''
                    if '@' in email_value:
                        cleaned_user['email'] = email_value
                        # Extract name from email prefix if no name provided
                        if 'name' not in cleaned_user:
                            cleaned_user['name'] = email_value.split('@')[0]
                elif key.lower() in ['name', 'full_name', 'username', 'user_name']:
                    cleaned_user['name'] = str(value).strip() if value else ''
                elif key.lower() in ['username', 'handle']:
                    cleaned_user['username'] = str(value).strip() if value else ''
                else:
                    # Keep original key but clean the value
                    cleaned_user[key.lower().replace(' ', '_')] = str(value).strip() if value else ''

            # Only include users with valid email addresses
            if cleaned_user.get('email') and '@' in cleaned_user['email']:
                # Add source if provided
                if source_name:
                    cleaned_user['source'] = source_name
                cleaned_data.append(cleaned_user)

        print(f"\n✅ Cleaned data: {len(cleaned_data)} users with valid emails")

        # Save to JSON file
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved to: {json_file}")

        # Show sample of cleaned data
        if cleaned_data:
            print(f"\n🔍 Sample cleaned user data:")
            sample_user = cleaned_data[0]
            for key, value in sample_user.items():
                print(f"  {key}: {value}")

        return True

    except Exception as e:
        print(f"❌ Error converting Excel to JSON: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Convert Excel file to JSON')
    parser.add_argument('input', nargs='?', default='luma R3world 活动邮箱.xlsx',
                       help='Input Excel file (default: luma R3world 活动邮箱.xlsx)')
    parser.add_argument('output', nargs='?', default='luma_r3world_users.json',
                       help='Output JSON file (default: luma_r3world_users.json)')
    parser.add_argument('--source', type=str, default=None,
                       help='Source identifier (optional)')
    args = parser.parse_args()

    print("🔄 Excel to JSON Converter")
    print("=" * 40)

    # Check if Excel file exists
    if not Path(args.input).exists():
        print(f"❌ Excel file not found: {args.input}")
        print("Available files:")
        for file in Path(".").glob("*.xlsx"):
            print(f"  - {file}")
        return

    # Convert Excel to JSON
    success = convert_excel_to_json(args.input, args.output, args.source)

    if success:
        print(f"\n🎉 Conversion completed successfully!")
        print(f"📄 JSON file created: {args.output}")
        print(f"💡 You can now use this file with your email campaigns")
    else:
        print(f"\n❌ Conversion failed!")

if __name__ == "__main__":
    main()