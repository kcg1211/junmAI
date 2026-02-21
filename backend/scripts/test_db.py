import chromadb
from app.core.config import settings

# Use the same path as your ingest_data.py
CHROMA_PATH = settings.CHROMA_PATH 

def test_query(search_term):
    # 1. Connect to the existing DB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    #TODO: add collection name into config.settings
    
    # 2. Get the collection
    collection = client.get_collection(name="sake_knowledge_base")
    
    # 3. Perform a search
    # This will return the 2 most relevant chunks
    results = collection.query(
        query_texts=[search_term],
        n_results=2
    )
    
    # 4. Print results
    print(f"\n--- Results for: '{search_term}' ---")
    for i in range(len(results['documents'][0])):
        content = results['documents'][0][i]
        metadata = results['metadatas'][0][i]
        print(f"\nResult {i+1}:")
        print(f"Source: {metadata['title']} ({metadata['url']})")
        print(f"Content: {content[:200]}...") # Print first 200 chars

# Run a test
if __name__ == "__main__":
    # Check if the total count matches your expectations
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    col = client.get_collection(name="sake_knowledge_base")
    print(f"Total chunks in database: {col.count()}")
    
    # Try searching for something specific from your data
    test_query("What is Hattan-nishiki?")
    test_query("How to define Acidity?")
    test_query("What is sake?")