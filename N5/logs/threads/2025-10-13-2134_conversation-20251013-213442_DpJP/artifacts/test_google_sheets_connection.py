#!/usr/bin/env python3
"""Test Google Sheets API connection."""
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define scope
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Authenticate
creds = ServiceAccountCredentials.from_json_keyfile_name(
    '/home/workspace/N5/config/credentials/google_service_account.json',
    scope
)
client = gspread.authorize(creds)

print("✓ Authentication successful!")
print(f"✓ Service account: {creds.service_account_email}")
print("\nReady to access Google Sheets.")
print("\nNext step: Share your Google Sheet with:")
print(f"  → {creds.service_account_email}")
