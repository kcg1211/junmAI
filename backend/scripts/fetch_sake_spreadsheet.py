from dotenv import load_dotenv
from pathlib import Path
import gspread
from gspread.exceptions import SpreadsheetNotFound, APIError
import pandas as pd
import json
import sys
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
    try: 
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

        if not data:
            print(f"Warning: The sheet '{SHEET_NAME}' is empty.")
            return

        # 3. Use Pandas for easy data handling
        df = pd.DataFrame(data)
        print("Data successfully fetched.")

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

        # 4. Save to JSON for the sake_engine.py to read

        # Use encoding='utf-8' and disable ensure_ascii to avoid garbage characters for Japanese words
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            df.to_json(f, orient='records', indent=4, force_ascii=False)
        print(f"Successfully synced {len(df)} sakes to {OUTPUT_FILE}")
    
    except SpreadsheetNotFound:
        print(f"Error: Could not find a sheet named '{SHEET_NAME}'. Check the name and sharing permissions.")
    except APIError as e:
        error_status = e.response.status_code
        if error_status == 403:
            print("Error 403: Insufficient permissions. Check API Scopes.")
        elif error_status == 429:
            print("Error 429: Rate limit exceeded. Try again in a minute.")
        else:
            print(f"Google API Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_sake_data()