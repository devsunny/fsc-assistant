import json
import logging
import os
import re
from copy import deepcopy
from datetime import date, datetime
from functools import partial
from pathlib import Path
from typing import Annotated, Callable, List, Optional, TypedDict, Union

# LangChain/LangGraph imports
import click
from prompt_toolkit import HTML, PromptSession
from prompt_toolkit import prompt as terminal_prompt
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from assistant.agents.postgresql.supervisor_agent import SupervisorAgent
from assistant.database.postgresql.client import PostgreSQLClient
from assistant.llm.history import LLMChatHistoryManager

from ..config.manager import AssistantConfig
from .text_to_sql_agent import TextToSQLAgent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PgAgentShell:
    def __init__(
        self,
        schema_context: Union[Path, str],
        dbclient: PostgreSQLClient,
        config: AssistantConfig = None,
        reload: bool = False,
    ):
        assistant_hist = Path.home() / ".assistant/.pg_t2s_prompt_history"
        if assistant_hist.exists() is False:
            assistant_hist.parent.mkdir(exist_ok=True)
            assistant_hist.write_text("")
        self.reload = reload
        self.prompt_history = FileHistory(assistant_hist.resolve())
        self.prompt_session = PromptSession(history=self.prompt_history)
        self.schema_context = (
            schema_context.read_text()
            if isinstance(schema_context, Path)
            else schema_context
        )
        self.config = config if config is not None else AssistantConfig()
        self.console = Console()
        history_file_path = Path.home() / ".fsc-assistant" / ".sql_to_text_history"
        self.chat_history_manager = LLMChatHistoryManager(
            history_file_path=history_file_path
        )
        self.text_to_sql_agent = TextToSQLAgent(
            database_schema=self.schema_context,
            dbclient=dbclient,
            config=self.config,
            reload_schema=self.reload,
            chat_history_manager=self.chat_history_manager,
        )
        self.llm_client = self.text_to_sql_agent.llm_client
        self.supervisor = SupervisorAgent(
            self.schema_context,
            self.text_to_sql_agent.llm_client.llm_models[0],
            self.llm_client,
            self.chat_history_manager,
        )

    def display_welcome(self):
        """Display welcome message and instructions"""
        welcome_text = """Welcome to the interactive Kara Code shell!
### Commands:
- Type your prompt and press Enter twice to submit
- Type 'exit' or 'quit' or 'bye' to leave
- Type 'clear' to clear CLI console screen
- Type 'clear history', 'save history', 'show history' to view, save and clear hsitory
- Press Ctrl+C to cancel current input

### Multi-line Input:
Enter your prompt. Press Enter twice (empty line) to submit.
        """
        self.console.print(Markdown(welcome_text))

    def get_multiline_input(self) -> Optional[str]:
        """Get multi-line input from user"""
        self.console.print(
            "\n[bold cyan]Enter your prompt (double Enter to submit):[/bold cyan]"
        )
        lines = []

        try:
            line_pos = 0
            while True:
                line_pos += 1
                if line_pos == 1:
                    line = self.prompt_session.prompt(
                        HTML("<ansiyellow>[You]&gt;&gt;&gt; </ansiyellow>")
                    )
                else:
                    line = self.prompt_session.prompt(
                        HTML("<ansiyellow>... </ansiyellow>")
                    )

                if (
                    len(lines) == 1
                    and lines[0].strip() in ["quit", "exit", "bye", "\\q"]
                    and line == ""
                ):
                    break
                elif line == "" and lines and lines[-1] == "":
                    lines.pop()  # Remove the last empty line
                    break
                lines.append(line)

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Input cancelled[/yellow]")
            return None

        prompt = "\n".join(lines).strip()
        return prompt if prompt else None

    def _show_history(self):
        hists = self.chat_history_manager.get_chat_history(40)
        for hist in hists:
            if hist.get("role") == "user":
                self.console.print(hist.get("content"))

    def process_command(self, command: str) -> bool:
        """Process special commands"""
        command_lower = command.lower().strip()

        if command_lower in ["exit", "quit", "q", "bye"]:
            self.console.print("[bold red]Goodbye![/bold red]")
            return False

        if command_lower == "clear":
            os.system("clear" if os.name == "posix" else "cls")
            self.display_welcome()
            return True

        if re.search(r"^clear\s*history$", command_lower) or re.search(
            r"new(\s*chat)?$", command_lower
        ):
            self.chat_history_manager.clear_history()
            return True

        if re.search(r"^save\s*history$", command_lower):
            self.chat_history_manager.save_history()
            return True

        if re.search(r"^show\s*history$", command_lower):
            self._show_history()
            return True

        return None

    @staticmethod
    def dict_list_to_markdown_table(data):
        """
        Convert a list of dictionaries to a markdown table format.

        Args:
            data (list): List of dictionaries with consistent keys

        Returns:
            str: Markdown formatted table string
        """
        if not data:
            return "No data available"

        # Get headers from the first dictionary
        headers = list(data[0].keys())

        # Create header row
        header_row = "| " + " | ".join(str(h) for h in headers) + " |"

        # Create separator row
        separator_row = "| " + " | ".join("---" for _ in headers) + " |"

        # Create data rows
        data_rows = []
        for item in data:
            row = "| " + " | ".join(str(item.get(h, "")) for h in headers) + " |"
            data_rows.append(row)

        # Combine all rows
        markdown_table = "\n".join([header_row, separator_row] + data_rows)

        return markdown_table

    def run(self):
        """Main loop for the interactive shell"""
        self.display_welcome()
        while True:
            try:
                # Get user input
                user_input = self.get_multiline_input()

                if user_input is None:
                    continue

                # Check for special commands
                command_result = self.process_command(user_input)
                if command_result is not None:
                    if not command_result:
                        break
                    continue

                # Call LLM API
                self.console.print("[green][Asisstant]: [/green]", end="")
                if self.supervisor.review_query(user_input) == "SQL_QUERY":
                    response = self.text_to_sql_agent.generate_and_execute_sql(
                        user_input
                    )

                    if not response:
                        self.console.print("[red]No response received[/red]")
                        continue
                    else:

                        if response.get("success"):
                            resp_str = self.dict_list_to_markdown_table(
                                response.get("data", [])
                            )
                            self.chat_history_manager.add_user_message(user_input)
                            self.chat_history_manager.add_assistant_message(resp_str)
                            self.console.print(
                                Panel(
                                    Markdown(resp_str),
                                    title="Query Result",
                                    subtitle=f"Rows: {response.get('row_count', 0)}",
                                )
                            )
                        else:
                            resp_str = response.get("error", "Unknown error")
                            self.chat_history_manager.add_user_message(user_input)
                            self.chat_history_manager.add_assistant_message(resp_str)
                            self.console.print(
                                Panel(Markdown(resp_str), title="Error Response")
                            )
                else:

                    resp_str = ""
                    for chunk in self.llm_client.invoke_model_generator(
                        model_id=self.llm_client.llm_models[0], prompt=user_input
                    ):
                        resp_str += chunk
                        print(chunk, end="", flush=True)
                    print("\n")
                    resp_str = resp_str.split("</thnk>")[
                        -1
                    ].strip()  # Clean up response
                    self.chat_history_manager.add_user_message(user_input)
                    self.chat_history_manager.add_assistant_message(resp_str)
                    self.console.print(Panel(Markdown(resp_str), title="Chat Response"))
                    # do regular chat here
                    pass

            except KeyboardInterrupt:
                self.console.print(
                    "\n[yellow]Use 'exit' or 'quit' to leave the shell[/yellow]"
                )
            except Exception as e:
                logger.exception("Error in main loop", exc_info=e)
                self.console.print(f"[red]Error: {str(e)}[/red]")


@click.command
def pg_agent_shell():
    """start an interactive LLM GenAI shell"""
    config = AssistantConfig()
    database = "database"
    schema_file = Path(
        "/home/liusu_admin/devel/atlas-phanes/tests/meta_dev_user_role.txt"
    )
    dbprop = config.get_section(database)
    if "url" in dbprop:
        database_url = dbprop["url"]
        del dbprop["url"]
        dbprop["database_url"] = database_url
    dbprop["max_conn"] = 1
    with PostgreSQLClient(**dbprop) as dbclient:
        shell = PgAgentShell(schema_file, dbclient, config)
        shell.run()


if __name__ == "__main__":
    # Example 1: Save a file, then load it back in the same session
    # shell = AgenticShell()
    # shell.run()
    pg_agent_shell()
