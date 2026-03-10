from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from app.services.rag_service import SakeRagService
from app.services.llm_service import SakeLlmService
from app.core.config import settings

CHROMA_PATH = settings.CHROMA_PATH 
app = FastAPI(title="junmAI - Sake Sommelier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

rag_service = SakeRagService(chroma_client)
llm_service = SakeLlmService()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

@app.get("/")
def read_root():
    return {"message": "junmAI Backend is running!"}

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    try:
        # 1. Get hybrid context (Plan -> Search -> Format)
        retrieved_context = await rag_service.get_hybrid_context(request.query)
        
        # 2. Generate final response via LLM
        answer = await llm_service.generate_final_response(
            user_query=request.query, 
            retrieved_context=retrieved_context
        )
        
        return QueryResponse(answer=answer)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)