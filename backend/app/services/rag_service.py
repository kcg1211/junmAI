from google import genai
import json
import random
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
        self.model_id = "gemini-3.1-flash-lite-preview"

    def generate_search_plan(self, user_query: str):
        """Uses Gemini 3.1 Flash to decompose the query into optimized search instructions."""
        
        system_prompt = """
        You are the Routing Brain for JunmAI, a Sake Sommelier assistant. 
        Analyze the query and output JSON only.
        
        JSON Schema:
        {
          "path": "general" | "suggestion" | "complex" | "out_of_scope",
          "suggestion_query": "Optimized keywords for bottle flavour/aroma (e.g., 'melon, crisp, fruity')",
          "knowledge_query": "Optimized keywords for general and technical definitions (e.g., 'polishing ratio explanation')",
          "filters": {
            "name": "String or null",
            "prefecture": "String or null",
            "polishing_ratio": "String or null",
            "rice_type": "String or null",
            "style": "sweet" | "medium sweet" | "medium dry" | "dry"
            "serving_temp": "cold" | "cold, ambient" | "cold, ambient, warm"
          }
        }

        Rules:
        - If the query is NOT about sake, alcohol brewing, Japanese food pairings, or sake culture, path is 'out_of_scope'. For example: 'What is the weather?', 'Who is the president?', or 'How to fix a car?' are 'out_of_scope'.
        - If the user asks for bottle picks, recommendations or food match, path is 'suggestion'.
        - If they ask for an explanation or definition of a term or concept about brewing, path is 'general'.
        - If they ask for both, path is 'complex'. 
        - For 'suggestion_query', focus on flavour profiles (Soft Specs) like aroma and palate (e.g., 'melon, crisp, fruit').
        - For 'knowledge_query', transform the user's question into technical sake terminology suitable for searching educational articles (e.g., turn 'how is sake made' into 'sake brewing process, fermentation stages, koji-kin').
        - For 'filters', extract specific regional or technical data (Hard Specs). 
        - Thesaurus Expansion for 'suggestion_query': For flavour profiles, come up with related words. For example, expand 'fruity' into related esters like 'apple, pear, banana, melon'; expand 'crisp' into 'clean, dry, sharp finish'. For food pairing, don't expand with sensory descriptions (e.g. savoury, umami) and sake style (e.g. sweet, versatile), but expand with cooking method and dishes. For example, expand 'chicken' into 'karaage chicken, chick skewers'; expand 'seafood' into 'salmon, scallops, sashimi'.
        - Technical Translation: For 'knowledge_query', translate 'civilian' questions into industry standards. For example, transform 'why is rice ground?' into 'seimai-buai purpose, starch concentration, lipids removal'.
        - Hard Spec Normalization: Extract 'prefecture' and 'rice_type' exactly. For example, if a user says 'around 50%', set 'polishing_ratio' to '50%' (String). Map city names like 'Kobe' to their Prefecture (e.g., 'Hyogo').
        - Semantic/Deterministic Separation: If the user only provides Hard Specs (like '50% polishing'), use a general term like 'sake' in the suggestion_query so the vector search has a baseline, while keeping the Hard Spec in filters. For example, if a user asks for 'Gifu sake', put 'Gifu' in the filters and keep it OUT of the 'suggestion_query' to prevent vector noise.
        - Temperature Mapping: If user mentions something like "hot", "warm", "atsukan", "kanshu" -> "cold, ambient, warm".
        
        Few-Shot Examples:

        User Query: "I want a fruity sake from Gifu, and what does rice polishing ratio mean?"
        Output: {
        "path": "complex",
        "suggestion_query": "fruity, apple, melon, floral, strawberry",
        "knowledge_query": "seimai-buai definition, rice polishing ratio meaning, sake brewing standards",
        "filters": {
            "name": null,
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
            "name": null,
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

        if plan.get('path') == 'out_of_scope':
            return "Not a sake-related query"
        
        suggestion_results = []
        knowledge_results = []

        # 2. Parallel Retrieval Logic
        # If 'complex', trigger BOTH. Otherwise, only one.
        
        # suggestions can still be made even the suggestion_query is empty, as long as there is value for filter (happens when user is only querying the spec / name of the sake)
        if plan['path'] in ['suggestion', 'complex']:
            active_filters = self.engine.build_filters(plan['filters'])

            # Ensure we have at least an empty string for the query_texts if null
            search_text = plan.get('suggestion_query') or ""
    
            # Only query if we have a search term OR active filters
            if search_text or active_filters:
                suggestion_results = self.suggestion_collection.query(
                    query_texts=[search_text] if search_text else [""], 
                    where=active_filters if active_filters else None,
                    # top-k (top 3)
                    n_results=3
                )
                # print(raw_results)
                # print("===========================")
                # # pick 3 results from 5 for a feeling of randomness
                # if raw_results and 'ids' in raw_results and len(raw_results['ids'][0]) > 0:
                #     indices = list(range(len(raw_results['ids'][0])))
                #     selected_indices = random.sample(indices, min(3, len(indices)))
                    
                #     # Reconstruct a results object with only the selected 3
                #     suggestion_results = {
                #         'ids': [[raw_results['ids'][0][i] for i in selected_indices]],
                #         'documents': [[raw_results['documents'][0][i] for i in selected_indices]],
                #         'metadatas': [[raw_results['metadatas'][0][i] for i in selected_indices]],
                #         'distances': [[raw_results['distances'][0][i] for i in selected_indices]]
                #     }

        if plan['path'] in ['general', 'complex'] and plan.get('knowledge_query'):
            # Use the LLM-generated 'knowledge_query'
            knowledge_results = self.knowledge_collection.query(
                query_texts=[plan['knowledge_query']],
                n_results=2
            )

        # Use the engine to format the final string
        return self.engine.format_for_llm(suggestion_results, knowledge_results)