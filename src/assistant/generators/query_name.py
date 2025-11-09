import json
import os

from ..llm.client import LLMClient


def create_query_name(query: str) -> str:

    prompt = f"""you are tasked to create meaningful name for given SQL query with:
        1. Name should be able to convey what does this query do
        2. Name should be short and meaningful
        3. Name should use plain english
        4. only generate ONE name
        5. output format plain text
        6. no commentary, notes and explanation in the output
        
        ```sql
        {query}        
        ```        
        """
    llm = LLMClient()
    resp = llm.invoke_model(prompt)
    response_text = json.loads(resp)
    return response_text
