import asyncio
import json
import chromadb
from app.services.rag_service import SakeRagService
from app.core.config import settings

CHROMA_PATH = settings.CHROMA_PATH 

async def run_local_test():
    print("🍶 Connecting to local ChromaDB...")
    
    # 1. Initialize the actual ChromaDB Client
    # Adjust host/port if you aren't using the default settings
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # 2. Ensure collections exist so the service doesn't crash on init
    # These names come from your settings.KNOWLEDGE_COLLECTION_NAME, etc.
    try:
        chroma_client.get_or_create_collection(name=settings.KNOWLEDGE_COLLECTION_NAME)
        chroma_client.get_or_create_collection(name=settings.SUGGESTION_COLLECTION_NAME)
        print("✅ Collections verified/created.")
    except Exception as e:
        print(f"⚠️ Warning during collection setup: {e}")

    # 3. Initialize your service with the real client
    service = SakeRagService(db_client=chroma_client)

    # 4. Define test scenarios to exercise the Routing Brain
    test_queries = [
        # "What is best season for sake?", 
        # "I want a sake that have a polishing ration larger than 60%" 
        # "Recommend a full-bodied sake and explain what makes a sake full-bodied"
        # "Ippin Junmai Daiginjo"
        # "A sake from Fukui with 50% polish ratio"
        # "Yamadanishiki"
        # "A medium sweet sake that pairs well with seafood"
        # "Warm sake that pairs with miso"
        # "Warm sake that pairs with seafood"
        "What makes a sake suitable for warming"
    ]

    print(f"\n{'#'*60}")
    print(f"{' '*15} STARTING JUNMAI RAG TEST")
    print(f"{'#'*60}\n")

    for query in test_queries:
        print(f"🔍 USER QUERY: \"{query}\"")
        
        try:
            # Step A: Check the LLM's Search Plan
            # This verifies if Gemini 1.5 Flash is correctly classifying and expanding terms
            print("\n--- 🧠 PHASE 1: LLM ROUTING & EXPANSION ---")
            plan = service.generate_search_plan(query)
            print(json.dumps(plan, indent=2))

            # Step B: Check Retrieval and Formatting
            # This triggers the actual ChromaDB .query() calls
            print("\n--- 📚 PHASE 2: LOCAL DB RETRIEVAL ---")
            context = await service.get_hybrid_context(query)
            
            print("FINAL CONTEXT FOR LLM:")
            print("-" * 30)
            print(context)
            print("-" * 30)

        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        print(f"\n{'='*60}\n")

if __name__ == "__main__":
    # Ensure your GEMINI_API_KEY is in your environment variables
    try:
        asyncio.run(run_local_test())
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    except Exception as e:
        print(f"💥 Fatal Error: {e}")