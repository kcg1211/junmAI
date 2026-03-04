import chromadb
import pandas as pd
import json
import os
import logging
import sys
from pathlib import Path
import uuid

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(BACKEND_DIR)

from app.core.config import settings

# --- Configuration ---
CHROMA_PATH = settings.CHROMA_PATH 
COLLECTION_NAME = settings.SUGGESTION_COLLECTION_NAME

DATA_DIR = BACKEND_DIR / "data" / "processed"
LOG_DIR = BACKEND_DIR / "data" / "logs"
LOG_PATH = LOG_DIR / "ingestion_errors.log"

logging.basicConfig(
    level=logging.ERROR,
    filename=str(LOG_PATH),
    filemode='a',               # 'a' for append (don't delete old logs), 'w' to overwrite
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 1. Configuration & Client Setup

def ingest_sake_data(json_file_path):
    # Initialize ChromaDB persistent client
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Create or get the collection
    # Using the default embedding function (all-MiniLM-L6-v2)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    # 2. Load the Sake Data
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except UnicodeDecodeError as e:
        print(f"Error: Could not decode file. Try checking if the file is saved as UTF-8. {e}")
        return
        
    # Ensure data is in a list format for processing
    sake_list = raw_data if isinstance(raw_data, list) else [raw_data]

    documents = []
    metadatas = []
    ids = []

    for sake in sake_list:
        item_name = sake.get("Item name")

        if not item_name:
            logging.error(f"Skipping entry: Missing 'Item name'. Data: {sake}")
            continue

        normalized_name = str(item_name).strip().lower()
        sake_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, normalized_name))

        # 3. Define the "Soft Specs" (Searchable Text)
        # We combine these so the vector search understands the 'vibe' and pairings
        searchable_text = (
            f"Name: {item_name}. "
            f"Body: {sake.get('Body', '')}. "
            f"Aroma: {sake.get('Aroma', '')}. "
            f"Aroma character: {sake.get('Aroma character', '')}. "
            f"Palate character: {sake.get('Palate character', '')}. "
            f"Notes: {sake.get('Other descriptions', '')}. "
            f"Pairs well with: {sake.get('Food Pairing', '')}."
        )
        
        # 4. Define the "Hard Specs" (Metadata Filters)
        # These allow for deterministic filtering (e.g., polishing ratio < 60%)
        metadata = {
            "name": item_name,
            "prefecture": sake.get("Prefecture", "Unknown"),
            "polishing_ratio": sake.get("Rice polishing ratio", "Not specified"),
            "rice_type": sake.get("Rice", "Not specified"),
            "style": sake.get("Style", "Unknown"),
            "serving_temp": sake.get("Serving temperature", "Unknown")
        }

        documents.append(searchable_text)
        metadatas.append(metadata)
        ids.append(sake_id)

    # 5. Add to ChromaDB
    try:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    except Exception as e:
        logging.error(f"Error ingesting data: {e}")
        print(f"Error ingesting data: {e}")
    
    print(f"Successfully ingested {len(ids)} sake profiles into {COLLECTION_NAME}.")

def preview_sake_shape(json_file_path):
    # 1. Load the raw data from your JSON-based DataFrame source
    # Added encoding='utf-8' to handle Japanese characters and special symbols
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except UnicodeDecodeError as e:
        print(f"Error: Could not decode file. Try checking if the file is saved as UTF-8. {e}")
        return
    
    # Handle both single objects and lists
    sake_list = raw_data if isinstance(raw_data, list) else [raw_data]
    
    print(f"--- PREVIEWING DATA SHAPE FOR {len(sake_list)} ITEM(S) ---")
    
    for sake in sake_list:
        item_name = sake.get("Item name")

        if not item_name:
            logging.error(f"Skipping entry: Missing 'Item name'. Data: {sake}")
            continue

        normalized_name = str(item_name).strip().lower()
        sake_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, normalized_name))

        # 2. Construct the "Document" (The Searchable Text / Soft Specs)
        # This is what gets converted into "embeddings" for semantic matching
        document_text = (
            f"Name: {item_name}. "
            f"Body: {sake.get('Body', '')}. "
            f"Aroma: {sake.get('Aroma', '')}. "
            f"Aroma character: {sake.get('Aroma character', '')}. "
            f"Palate character: {sake.get('Palate character', '')}. "
            f"Notes: {sake.get('Other descriptions', '')}. "
            f"Pairs well with: {sake.get('Food Pairing', '')}."
        )

        # 3. Construct the "Metadata" (The Hard Filters / Deterministic Specs)
        # These are used for exact keyword/value matching 
        metadata = {
            "name": item_name,
            "prefecture": sake.get("Prefecture"),
            "polishing_ratio": sake.get("Rice polishing ratio"),
            "serving_temp": sake.get("Serving temperature")
        }

        # 4. Display the Shape
        print(f"\n[ID]: {sake_id}")
        print("-" * 30)
        print("VECTOR SEARCH TEXT (DOCUMENT):")
        print(f"> {document_text}")
        print("\nFILTERABLE DATA (METADATA):")
        print(metadata)
        print("=" * 50)

if __name__ == "__main__":
    # Point to your sample JSON file
    DATA_PATH = DATA_DIR / "sake_spreadsheet.json"
    ingest_sake_data(DATA_PATH)