import json
from pathlib import Path
from typing import Union

from assistant.llm.client import LLMClient
from assistant.llm.history import LLMChatHistoryManager
from assistant.utils.json import extract_json_from_text


class SupervisorAgent:
    def __init__(
        self,
        schema_context: Union[Path, str],
        llm_model: str,
        llm_client: LLMClient,
        chat_history_manager: LLMChatHistoryManager,
    ):
        self.llm_model = llm_model
        self.llm_client = llm_client
        self.chat_history_manager = chat_history_manager
        self.max_retries = 3
        self.schema_context = (
            schema_context.read_text()
            if isinstance(schema_context, Path)
            else schema_context
        )

    def review_query(self, user_question: str) -> str:
        prompt = f"""You are a system analyst. Your task is to review the the user's question and past chats to determine if it is asking for querying a database. or it is asking for some other information.
        
        ## Here is the database schema context:
        {self.schema_context}
        
        ## USER QUESTION:
        <!user_question!>
        {user_question}
        </!user_question!>
        
        ## OUTPUT FORMAT: json
        
        If the question is asking for querying a database, output "SQL_QUERY".
        If the question is asking for some other information, output "GENERAL_INFO".
        
        ## EXAMPLES:
        
        Question: "What is the total sales for last month?"
        Output: 
        {{
            "type": "SQL_QUERY"
        }}
        
        Question: "Who is the president of the United States?"
        Output:         
        {{
            "type": "GENERAL_INFO"      
        }}
        
        important note: do not include any explanation or extra information, only output the json object as specified.        
        """

        hist_msgs = self.chat_history_manager.get_chat_history(5)
        hist_msgs.append({"role": "user", "content": prompt})

        for attempt in range(1, self.max_retries + 1):
            response = ""
            for chunk in self.llm_client.invoke_model_generator(
                model_id=self.llm_model, messages=hist_msgs
            ):
                response += chunk
                print(chunk, end="", flush=True)
            print("\n")

            response = response.split("</thnk>")[-1].strip()  # Clean up response
            try:

                response_json = json.loads(extract_json_from_text(response))
                if "type" in response_json:
                    return response_json["type"]
                else:
                    print(
                        f"Attempt {attempt}: 'type' field not found in response. Retrying..."
                    )
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt}: JSON decode error: {e}. Retrying...")

        return "GENERAL_INFO"
