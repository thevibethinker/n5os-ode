#!/usr/bin/env python3
"""Test access to the actual Google Sheet."""
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_ID = "17I5UgjvtEcACsskMt9_tFac5-l9acyh3Nryp1HOttAs"

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/home/workspace/N5/config/credentials/google_service_account.json',
    scope
)

client = gspread.authorize(creds)

print(f"Testing access to sheet: {SHEET_ID}")
print("-" * 60)

try:
    # Open the sheet
    sheet = client.open_by_key(SHEET_ID)
    print(f"✓ Successfully opened sheet: '{sheet.title}'")
    
    # Get first worksheet
    worksheet = sheet.get_worksheet(0)
    print(f"✓ Found worksheet: '{worksheet.title}'")
    
    # Read headers
    headers = worksheet.row_values(1)
    print(f"✓ Headers: {headers}")
    
    # Count existing rows
    all_values = worksheet.get_all_values()
    row_count = len(all_values)
    print(f"✓ Current row count: {row_count}")
    
    # Show first few rows (if any)
    if row_count > 1:
        print(f"\n✓ Sample data (first row):")
        print(f"  {all_values[1]}")
    
    print("\n" + "="*60)
    print("SUCCESS! Full read/write access confirmed.")
    print("="*60)
    
except gspread.exceptions.SpreadsheetNotFound:
    print("✗ ERROR: Sheet not found or not shared with service account")
    print(f"  Make sure you shared the sheet with:")
    print(f"  job-sourcing-bot@applyai-dev.iam.gserviceaccount.com")
    
except gspread.exceptions.APIError as e:
    print(f"✗ API Error: {e}")
    print("\nPossible causes:")
    print("  1. Google Sheets API not enabled")
    print("  2. Google Drive API not enabled")
    print("  3. Sheet not shared with service account")
    
except Exception as e:
    print(f"✗ Unexpected error: {e}")
