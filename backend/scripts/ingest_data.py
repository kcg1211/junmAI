import json
import uuid
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.append(BACKEND_DIR)

from app.core.config import settings

#TODO: progress bar for ingestion (tqdm)

# --- Configuration ---
# Instead of hardcoded "./backend/chroma_db"
CHROMA_PATH = settings.CHROMA_PATH 
COLLECTION_NAME = settings.COLLECTION_NAME

DATA_DIR = BACKEND_DIR / "data" / "processed"

def load_jsonl(file_path):
    """Loads a .jsonl file and returns a list of dictionaries."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def load_json(file_path):
    """Loads a standard .json file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def standardize_data(raw_data, source_type):
    """
    Converts different source formats into a uniform dictionary.
    Required keys: 'content', 'title', 'source_url', 'metadata'
    """
    standardized = []
    
    for item in raw_data:
        if source_type == "glossary":
            # Mapping source2_data.json keys
            standardized.append({
                "content": f"{item['term']}: {item['description']}",
                "title": item['term'],
                "source_url": "https://japansake.or.jp/sake/en/basic/glossary/",
                "type": "definition"
            })
        elif source_type == "articles":
            # Mapping source1_data.jsonl and source3_data.jsonl [cite: 21, 441]
            standardized.append({
                "content": item.get('full_text', item.get('summary', '')), # Fallback to 'summary' if 'full_text is not found
                "title": item.get('title', 'Untitled'),
                "source_url": item.get('url', 'unknown'),
                "type": "article"
            })
            
    return standardized

def chunk_text(standardized_list):
    """Splits long content into manageable pieces for the Vector DB."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    
    chunks = []
    for item in standardized_list:
        # Split the standardized 'content'
        texts = text_splitter.split_text(item['content'])
        for i, text in enumerate(texts):
            chunks.append({
                "content": text,
                "metadata": {
                    "title": item['title'],
                    "url": item['source_url'],
                    "type": item['type'],
                    "chunk_id": i
                }
            })
    return chunks

def main():
    # 1. Initialize ChromaDB [cite: 7]
    client = chromadb.PersistentClient(path=CHROMA_PATH) # creating chromadb
    collection = client.get_or_create_collection(name="sake_knowledge_base")

    # 2. Load Raw Data
    print("Loading data sources...")
    raw_s1 = load_jsonl(DATA_DIR / "source1_data.jsonl") # [cite: 21]
    raw_s2 = load_json(DATA_DIR / "source2_data.json") #
    raw_s3 = load_jsonl(DATA_DIR / "source3_data.jsonl") # [cite: 441]

    # 3. Standardize
    print("Standardizing formats...")
    clean_data = []
    clean_data.extend(standardize_data(raw_s1, "articles"))
    clean_data.extend(standardize_data(raw_s2, "glossary"))
    clean_data.extend(standardize_data(raw_s3, "articles"))

    # 4. Chunking 
    print("Chunking long texts...")
    final_chunks = chunk_text(clean_data)
    
    #  Output and Inspect Chunks
    print(f"Total chunks created: {len(final_chunks)}")
    
    # Save to a file for manual review
    debug_file = DATA_DIR / "debug_chunks.json"
    with open(debug_file, "w", encoding="utf-8") as f:
        json.dump(final_chunks, f, indent=4, ensure_ascii=False)
    print(f"Full chunk data saved to: {debug_file}")

    # Print the first 2 chunks to the console for a quick check
    for i, chunk in enumerate(final_chunks[:2]):
        print(f"\n--- DEBUG CHUNK {i+1} ---")
        print(f"Source: {chunk['metadata']['title']}")
        print(f"Content Sample: {chunk['content'][:150]}...")

    # 5. Embed & Store [cite: 7]
    print(f"Ingesting {len(final_chunks)} chunks into ChromaDB...")
    for chunk in final_chunks:
        collection.add(
            documents=[chunk['content']],
            metadatas=[chunk['metadata']],
            ids=[str(uuid.uuid4())]
        )
    
    print("Ingestion complete!")

if __name__ == "__main__":
    print(f"Backend Directory: {BACKEND_DIR}")
    
    if not DATA_DIR.exists():
        print(f"Critical: {DATA_DIR} not found.")
    else:
        main()