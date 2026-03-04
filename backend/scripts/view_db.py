import chromadb
from app.core.config import settings
import os
import json

CHROMA_PATH = settings.CHROMA_PATH 
COLLECTION_NAME = settings.SUGGESTION_COLLECTION_NAME
OUTPUT_DIR = './data/processed'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'db_select_all2.json')

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(name=COLLECTION_NAME)

results = collection.get(
    include=["documents", "metadatas"]
)

try:
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"Successfully saved {len(results)} items to db_select_all2.json")
except IOError as e:
    print(f"Error writing to file: {e}")