class SakeEngine:
    def build_filters(self, filter_dict: dict):
        """Clean up null filters and wrap multiple filters for ChromaDB."""
        # 1. Remove None values
        active_filters = {k: v for k, v in filter_dict.items() if v is not None}
        
        # 2. Handle ChromaDB requirements for multiple filters
        if len(active_filters) > 1:
            return {
                "$and": [{k: v} for k, v in active_filters.items()]
            }
        
        # 3. Return single filter as-is (or None if empty)
        return active_filters if active_filters else None

    def format_for_llm(self, suggestion_results, knowledge_results):
        """The 'Stringifier': Turns raw DB results into a readable prompt block."""
        context_parts = []
        
        # 1. Process Sake Suggestion
        if suggestion_results and len(suggestion_results['documents'][0]) > 0:
            print(suggestion_results)
            context_parts.append("### SAKE SUGGESTIONS:")
            # ChromaDB returns a list of lists; we iterate through the first index
            for doc, meta in zip(suggestion_results['documents'][0], suggestion_results['metadatas'][0]):
                # Formatting as a clean list item
                context_parts.append(f"- PRODUCT: {doc} | SPECS: {meta}")

        # 2. Process Educational Knowledge (Brewing, Terms, Culture)
        if knowledge_results and len(knowledge_results['documents'][0]) > 0:
            context_parts.append("\n### SAKE KNOWLEDGE :")
            for doc in knowledge_results['documents'][0]:
                context_parts.append(f"- {doc}")
                
        # Return a single cohesive string or a fallback message
        if not context_parts:
            return "No specific sake or knowledge found for this query."
            
        return "\n".join(context_parts)