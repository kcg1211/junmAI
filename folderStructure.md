sake-ai-chatbot/
├── backend/                # Python FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # Entry point for the FastAPI server
│   │   ├── api/            # API Route definitions (e.g., /ask, /suggest)
│   │   │   └── endpoints/
│   │   ├── services/       # Core Logic (The "Brain")
│   │   │   ├── llm_service.py    # OpenAI/Gemini integration
│   │   │   ├── rag_service.py    # Searching the Vector DB
│   │   │   └── sake_engine.py    # Logic for filtering the Excel data
│   │   ├── models/         # Pydantic schemas for API requests/responses
│   │   └── core/           # Config, environment variables, and security
│   ├── requirements.txt
│   └── .env                # API Keys (OpenAI, Database URLs)
├── data/
│   ├── raw/                # Original Excel files (sake_list.xlsx)
│   └── processed/          # Cleaned JSON or locally cached data
├── scripts/                # Development & Data Maintenance scripts
│   ├── scraper.py          # Script to crawl sake websites
│   └── ingest_data.py      # Script to embed data and upload to Vector DB
├── frontend/               # UI (React, Vue, or Streamlit)
│   ├── public/
│   ├── src/
│   └── package.json
├── docker-compose.yml      # (Optional) To run DB and Backend together
├── .gitignore
└── README.md