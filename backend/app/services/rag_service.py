from google import genai
import json
import os
from app.services.sake_engine import SakeEngine
from app.core.config import settings

GENERAL_KNOWLEDGE = settings.KNOWLEDGE_COLLECTION_NAME
SAKE_SUGGESTION = settings.SUGGESTION_COLLECTION_NAME

class SakeRagService:
    def __init__(self, db_client):
        self.db = db_client
        self.knowledge_collection = self.db.get_collection(GENERAL_KNOWLEDGE)
        self.suggestion_collection = self.db.get_collection(SAKE_SUGGESTION)
        self.engine = SakeEngine()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = "gemini-2.5-flash"

    def generate_search_plan(self, user_query: str):
        """Uses Gemini 2.5 Flash to decompose the query into optimized search instructions."""
        
        system_prompt = """
        You are the Routing Brain for JunmAI, a Sake Sommelier assistant. 
        Analyze the query and output JSON only.
        
        JSON Schema:
        {
          "path": "general" | "suggestion" | "complex",
          "suggestion_query": "Optimized keywords for bottle flavour/aroma (e.g., 'melon, crisp, fruity')",
          "knowledge_query": "Optimized keywords for general and technical definitions (e.g., 'polishing ratio explanation')",
          "filters": {
            "prefecture": "String or null",
            "polishing_ratio": "String or null",
            "rice_type": "String or null",
            "style": "String or null",
            "serving_temp": "String or null"
          }
        }

        Rules:
        - If the user asks for bottle picks, recommendations or food match, path is 'suggestion'.
        - If they ask for an explanation or definition of a term or concept about brewing, path is 'general'.
        - If they ask for both, path is 'complex'. 
        - For 'suggestion_query', focus on flavour profiles (Soft Specs) like aroma and palate (e.g., 'melon, crisp, fruit').
        - For 'knowledge_query', transform the user's question into technical sake terminology suitable for searching educational articles (e.g., turn 'how is sake made' into 'sake brewing process, fermentation stages, koji-kin').
        - For 'filters', extract specific regional or technical data (Hard Specs). 
        - Thesaurus Expansion: For 'suggestion_query', do not just repeat the user's words. For example, expand 'fruity' into related esters like 'apple, pear, banana, melon'; expand 'crisp' into 'clean, dry, sharp finish'.
        - Technical Translation: For 'knowledge_query', translate 'civilian' questions into industry standards. For example, transform 'why is rice ground?' into 'seimai-buai purpose, starch concentration, lipids removal'.
        - Hard Spec Normalization: Extract 'prefecture' and 'rice_type' exactly. For example, if a user says 'around 50%', set 'polishing_ratio' to '50%' (String). Map city names like 'Kobe' to their Prefecture (e.g., 'Hyogo').
        - Semantic/Deterministic Separation: If the user only provides Hard Specs (like '50% polishing'), use a general term like 'sake' in the suggestion_query so the vector search has a baseline, while keeping the Hard Spec in filters. For example, if a user asks for 'Gifu sake', put 'Gifu' in the filters and keep it OUT of the 'suggestion_query' to prevent vector noise.
        
        Few-Shot Examples:

        User Query: "I want a fruity sake from Gifu, and what does rice polishing ratio mean?"
        Output: {
        "path": "complex",
        "suggestion_query": "fruity, apple, melon, floral, strawberry",
        "knowledge_query": "seimai-buai definition, rice polishing ratio meaning, sake brewing standards",
        "filters": {
            "prefecture": "Gifu",
            "polishing_ratio": null,
            "rice_type": null,
            "style": null,
            "serving_temp": null
            }
        }

        User Query: "Recommend something crisp that pairs with salmon under 50% polishing."
        Output: {
        "path": "suggestion",
        "suggestion_query": "crisp, clean finish, dry, salmon pairing, seafood match",
        "knowledge_query": null,
        "filters": {
            "prefecture": null,
            "polishing_ratio": "50%",
            "rice_type": null,
            "style": null,
            "serving_temp": null
            }
        }
        
        """

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=f"{system_prompt}\n\nUser Query: {user_query}",
            config={
                "response_mime_type": "application/json",
            }
        )

        return json.loads(response.text)

    async def get_hybrid_context(self, user_query: str):
        # 1. Get the dynamic plan from Gemini
        plan = self.generate_search_plan(user_query)
        
        suggestion_results = []
        knowledge_results = []

        # 2. Parallel Retrieval Logic
        # If 'complex', trigger BOTH. Otherwise, only one.
        
        # FIX: Trigger if path is correct, regardless of whether suggestion_query is null
        if plan['path'] in ['suggestion', 'complex']:
            active_filters = self.engine.build_filters(plan['filters'])
            
            # Ensure we have at least an empty string for the query_texts if null
            search_text = plan.get('suggestion_query') or ""
            
            # Only query if we have a search term OR active filters
            if search_text or active_filters:
                suggestion_results = self.suggestion_collection.query(
                    query_texts=[search_text] if search_text else [""], 
                    where=active_filters if active_filters else None,
                    n_results=3
                )

        if plan['path'] in ['general', 'complex'] and plan.get('knowledge_query'):
            # Use the LLM-generated 'knowledge_query'
            knowledge_results = self.knowledge_collection.query(
                query_texts=[plan['knowledge_query']],
                n_results=2
            )

        # Use the engine to format the final string
        return self.engine.format_for_llm(suggestion_results, knowledge_results)