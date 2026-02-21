from dotenv import load_dotenv
from pathlib import Path
import gspread
import pandas as pd
import json
import os
from google.oauth2.service_account import Credentials

load_dotenv()

# 1. Setup paths based on your folder structure
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CREDENTIALS_FILE = PROJECT_ROOT / os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
OUTPUT_DIR = './data/processed'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'sake_spreadsheet.json')
SHEET_NAME = "junmAI sake list"

def fetch_sake_data():
    # Define the scope for Google Sheets access
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.metadata.readonly"
        ]
    
    # Authenticate using the service account 
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)

    # 2. Open the sheet and get all records 
    sheet = client.open(SHEET_NAME).sheet1
    data = sheet.get_all_records()

    # 3. Use Pandas for easy data handling
    df = pd.DataFrame(data)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # 4. Save to JSON for the sake_engine.py to read
    df.to_json(OUTPUT_FILE, orient='records', indent=4)
    print(f"Successfully synced {len(df)} sakes to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_sake_data()