JunmAI: Your virtual Sake Sommelier

JunmAI is an AI-powered chatbot designed to bridge the gap between traditional Japanese sake expertise and modern digital accessibility. By combining professional sommelier knowledge with Retrieval-Augmented Generation (RAG), JunmAI provides accurate, data-driven sake recommendations and information.

## Project Overview
Selecting the perfect sake can be intimidating, whether you are a novice or a seasoned enthusiast. JunmAI simplifies this process through two core functions:

- Sake Knowledge Base: Users can ask any question regarding sake. From brewing methods to regional styles, and receive answers grounded in verified, scraped content from authoritative sake websites.

- Intelligent Recommendations: Whether a user has a "vague preference" or needs a "serious match" for a specific dish, the bot analyses a curated database of sake profiles (including polishing ratios, palate, and aroma) to suggest the ideal bottle.

## Technical Architecture
JunmAI is built using a modern Python-based FastAPI backend and a decoupled frontend, utilising a RAG (Retrieval-Augmented Generation) pipeline to ensure data grounded in factual sake knowledge.

### The Tech Stack

- Backend: FastAPI (Python) for high-performance asynchronous API endpoints.

- Frontend: Mobile-First React Interface optimised for mobile browsers, providing diners with a fast, responsive interface to navigate complex sake lists directly from their restaurant table.

- Intelligence: LLM integration for natural language understanding, context generation, and generative response.

- Vector Database: ChromaDB for storing and retrieving embedded web content and spreadsheet.

- Web Scraping: BeautifulSoup for converting HTML from authoritative sources into clean, processable text.


## Project Structure

```
junmAI/
├── backend/                # FastAPI Server
│   ├── app/
│   │   ├── core/           # Pydantic validation settings
│   │   └── services/       # Core Logic (LLM, RAG, and Sake Engine)
├── data/
│   └── processed/          # Cleaned data for ingestion
├── scripts/                # Scraper and Data Ingestion tools
├── chroma_db/              # Local Vector Database storage
└── frontend/               # UI (React)
```

## System Design
![junmAI System Design Diagram](https://drive.google.com/uc?export=view&id=12qEysJtKFx515CtNb9d4EvnZZfCbWFKF)

## Roadmap

| Phase | Focus | Key Deliverables |
| :--- | :--- | :--- |
| **1. Data** | Grounding Truth | Web scraping, sake list Excel processing, ChromaDB ingestion. 
| **2. LLM** | Intelligence | OpenAI/Gemini RAG integration and "context-only" prompt engineering. | **(currently here)** |
| **3. API** | Logic & Routing | FastAPI endpoints for functionalities. |
| **4. Interface** | User Experience | Mobile-based UI to facilitate interactive sake consultations. |




