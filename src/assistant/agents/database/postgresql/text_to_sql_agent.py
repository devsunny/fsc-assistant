# agents/text_to_sql_agent.py
# Requires: openai

from pathlib import Path
from typing import Any, Dict, Optional, Union

from openai import OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit import prompt as terminal_prompt
from prompt_toolkit.history import FileHistory

from assistant.agents.postgresql.supervisor_agent import SupervisorAgent
from assistant.database.postgresql.client import PostgreSQLClient
from assistant.llm.client import LLMClient
from assistant.llm.history import LLMChatHistoryManager

from ..config.manager import AssistantConfig
from .prompt_builder import SQLPromptBuilder
from .sql_executor_agent import SQLExecutorAgent

MAX_SQL_RETRY_ATTEMPTS = 3


class TextToSQLAgent:
    def __init__(
        self,
        database_schema: Union[Path, str],
        dbclient: PostgreSQLClient,
        config: AssistantConfig = None,
        reload_schema: bool = False,
        chat_history_manager: LLMChatHistoryManager = None,
    ):
        self.config = config if config is not None else AssistantConfig()
        self.base_url = self.config.get_option("llm", "base_url")
        self.llm_provider = self.config.get_option("llm", "provider") or "proxy"
        self.api_key = self.config.get_option("llm", "api_key")
        self.max_completion_tokens = self.config.get_int(
            "llm", "max_completion_tokens", default=32000
        )
        self.selected_model = self._get_selected_model()
        self.prompt_session = self._create_prompt_session()
        self.prompt_builder = SQLPromptBuilder(database_schema, reload_schema)
        self.llm_client = LLMClient()
        self.executor_agent = SQLExecutorAgent(dbclient)
        self.chat_history_manager = (
            chat_history_manager
            if chat_history_manager is not None
            else LLMChatHistoryManager()
        )

    def _get_selected_model(self) -> str:
        models = self.config.get_option("llm", "models")
        assert (
            models is not None and len(models) > 0
        ), f"please config LLM models in {AssistantConfig.CONFIG_FILENAME}"
        self.llm_models = [models] if isinstance(models, str) else models
        return models[0]

    def _create_prompt_session(self) -> PromptSession:
        assistant_hist = Path.home() / ".assistant/.kara_prompt_history"
        if assistant_hist.exists() is False:
            assistant_hist.parent.mkdir(exist_ok=True)
            assistant_hist.write_text("")

        self.prompt_history = FileHistory(assistant_hist.resolve())
        return PromptSession(history=self.prompt_history)

    def _database_config(self) -> Dict[str, Any]:
        dbprop = self.config.get_section("database")
        assert (
            dbprop is not None
        ), f"please config database in {AssistantConfig.CONFIG_FILENAME}"
        if "url" in dbprop:
            database_url = dbprop["url"]
            del dbprop["url"]
            dbprop["database_url"] = database_url
        dbprop["max_conn"] = 1
        return dbprop

    def _clean_sql(self, sql: str) -> str:
        sql = sql.strip()
        if sql.startswith("```sql"):
            sql = sql[6:]
        elif sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        sql = sql.strip()
        if sql.endswith(";"):
            sql = sql[:-1]
        return sql

    def generate_and_execute_sql(self, user_query: str) -> Dict[str, Any]:
        prompt = self.prompt_builder.build_initial_prompt(user_query)
        for attempt in range(1, MAX_SQL_RETRY_ATTEMPTS + 1):
            sql_response = ""
            for chunk in self.llm_client.invoke_model_generator(prompt=prompt):
                sql_response += chunk
                print(chunk, end="", flush=True)
            print("\n")
            sql = self._clean_sql(sql_response)

            result = self.executor_agent.execute_and_validate(sql)

            if result["success"]:
                return {
                    "success": True,
                    "query": user_query,
                    "sql": sql,
                    "data": result["data"],
                    "columns": result["columns"],
                    "row_count": result["row_count"],
                    "attempts": attempt,
                }

            if attempt < MAX_SQL_RETRY_ATTEMPTS:
                feedback = self.executor_agent.get_feedback_for_llm(result)
                prompt = self.prompt_builder.build_fix_prompt(
                    user_query, sql, result["error"], attempt + 1
                )
            else:
                return {
                    "success": False,
                    "query": user_query,
                    "sql": sql,
                    "error": result["error"],
                    "error_type": result["error_type"],
                    "attempts": attempt,
                    "message": "Maximum retry attempts reached",
                }

        return {
            "success": False,
            "query": user_query,
            "message": "Failed to generate valid SQL",
            "attempts": MAX_SQL_RETRY_ATTEMPTS,
        }
