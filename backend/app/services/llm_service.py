from google import genai
from app.core.config import settings

class SakeLlmService:
    def __init__(self):
        # Initialize the Gemini client using your existing configuration
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = "gemini-3.1-flash-lite-preview" 

    async def generate_final_response(self, user_query: str, retrieved_context: str):
        """
        Synthesizes the final conversational response based on RAG context.
        """
        
        system_prompt = """
        YOU ARE JUNMAI: A professional Japanese Sake Sommelier.
        
        GOAL:
        Provide accurate, data-driven sake recommendations and information based ONLY on the provided context.
        
        STRICT RULES (Constraint Enforcement):
        1. SAKE SUGGESTIONS: Use the 'SAKE SUGGESTIONS' list to provide recommendations. 
        2. SINGLE RANDOM SELECTION: If the 'SAKE SUGGESTIONS' list contains multiple bottles, you must RANDOMLY choose only ONE bottle to recommend. Do not mention the others or provide a list.
        3. EXCLUSIVITY: If a sake name is not in the provided list, do not recommend it. If the list is empty, inform the user that no matching bottles.
        4. KNOWLEDGE: Use 'SAKE KNOWLEDGE' to explain technical terms (e.g., polishing ratio, brewing methods).
        5. TONE: Be helpful, sophisticated, and encouraging. Use professional sommelier language (e.g., 'palate', 'aroma', 'finish').
        6. FORMATTING: bold the names of the sake.
        7. FALLBACK HANDLING: If the context received is "No result found for this query." or "Not a sake-related query", do not use those exact phrases. Instead, politely paraphrase them for the user in your sommelier persona. Explain that your expertise is currently limited to specific curated sakes or that the query is outside your sake-specialized knowledge.

        """

        # Construct the final prompt for the LLM
        # This combines the "Stringified" block from your sake_engine and the user's original intent
        user_message = f"""
        CONTEXT FROM DATABASE:
        {retrieved_context}

        USER QUESTION: 
        {user_query}

        RESPONSE:
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=user_message,
                config={
                    "system_instruction": system_prompt,
                    "temperature": 0.3,  # Lower temperature for higher factual consistency
                }
            )
            return response.text
            
        except Exception as e:
            return f"I apologize, I encountered an error while consulting my records: {str(e)}"