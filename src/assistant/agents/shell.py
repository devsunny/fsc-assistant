"""Interactive shell for the Kara Code AI assistant.

This module provides an interactive command-line interface for interacting with
the Kara Code AI assistant. It supports multi-line input, command history,
document analysis, and various special commands.
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from ..config.manager import AssistantConfig
from assistant.utils.cli.console import get_cli_console
from assistant.utils.cli.executor import execute_command_realtime_combined, execute_command_realtime_threaded, execute_command_with_output
from assistant.utils.path import get_project_root

# Defer heavy imports until needed
if TYPE_CHECKING:
    from ..llm.agent_client import AgentOrchestrator

from . import shell_constants as const
from . import shell_help

from .utils.prompts import CODING_ASSISTANT_SYSTEM_PROMPT
from .query_analyzer import analyze_user_intent, Intent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AgenticShell:
    """
    Interactive shell for the FSC Assistant.

    Provides a command-line interface for interacting with LLM models,
    managing conversation history, executing system commands, and accessing
    various AI-powered tools.

    Attributes:
        console: Rich Console for formatted output
        config: Kara Code configuration
        llm: Agent orchestrator for LLM interactions
        tools_repository: Repository of available tools
        tool_selector: Optional tool selector for intelligent tool selection
        selected_model: Currently active LLM model
        last_command_output: Stores the output of the most recently executed command
    """

    def __init__(self, config: Optional[AssistantConfig] = None) -> None:
        """
        Initialize the Agentic Shell.

        Args:
            config: Optional Kara Code configuration. If None, loads default config.

        Raises:
            AssertionError: If no LLM models are configured.
        """
        self.console = Console()
        self.config = config if config is not None else AssistantConfig()
        self.cliconsole = get_cli_console()
        
        # Defer heavy LLM initialization until first use
        self._llm = None
        self._selected_model = None
        self._cached_tools = None
        self.last_command_output = None
    
    # lambda x: print(x, end="", flush=True),
    @property
    def llm(self) -> 'AgentOrchestrator':
        """Lazy-loaded AgentOrchestrator instance."""
        if self._llm is None:
            from ..llm.agent_client import AgentOrchestrator
            self._llm = AgentOrchestrator(
                stream_handler= lambda x: print(x, end="", flush=True),
                debug=os.environ.get("DEBUG", "False").lower() == "true",
                config=self.config,
            )
            self._selected_model = self._llm.model
        return self._llm

    @property
    def selected_model(self) -> str:
        """Get the currently selected model."""
        if self._selected_model is None:
            # This will trigger llm initialization
            _ = self.llm
        return self._selected_model

    @selected_model.setter
    def selected_model(self, value: str) -> None:
        """Set the selected model."""
        self._selected_model = value
        if self._llm is not None:
            self._llm.model = value

    def switch_model(self, model_id: str) -> str:
        """
        Switch to a different LLM model during runtime.

        Args:
            model_id: Identifier of the model to switch to

        Returns:
            Confirmation message with old and new model names
        """
        old_model = self.selected_model
        logger.info(f"Switching model from {old_model} to {model_id}")
        self.selected_model = model_id
        self.llm.model = self.selected_model
        return f"Switched model from {old_model} to {model_id}"

    def show_current_model(self) -> str:
        """
        Get the current selected LLM model.

        Returns:
            Name of the currently selected model
        """
        return self.selected_model

    def is_document_analysis_request(self, user_input: str) -> bool:
        """
        Check if user input is a document analysis request.

        Detects requests that mention document file extensions combined with
        analysis keywords like "explain", "summarize", "describe".

        Args:
            user_input: User's input text

        Returns:
            True if this appears to be a document analysis request
        """
        doc_exts = const.DOCUMENT_EXTENSIONS
        lower_user_input = user_input.lower()
        for ext in doc_exts:
            if ext in lower_user_input and any(
                keyword in lower_user_input
                for keyword in const.DOCUMENT_ANALYSIS_KEYWORDS
            ):
                return True
        return False

    def is_document_extraction_request(self, user_input: str) -> bool:
        """
        Check if user input is a document extraction request.

        Detects requests that mention document file extensions combined with
        extraction keywords like "extract".

        Args:
            user_input: User's input text

        Returns:
            True if this appears to be a document extraction request
        """
        doc_exts = const.DOCUMENT_EXTENSIONS
        lower_user_input = user_input.lower()
        for ext in doc_exts:
            if any(
                keyword in lower_user_input
                for keyword in const.DOCUMENT_EXTRACTION_KEYWORDS
            ):
                return True
        return False

    def get_system_prompt(self, user_input: Optional[str] = None) -> str:
        """
        Get the appropriate system prompt based on the user input.

        Returns different system prompts for:
        - Document analysis requests
        - OpenSpec commands (loads AGENTS.md)
        - General coding assistance (default)

        Args:
            user_input: User's input text, used to determine prompt type

        Returns:
            System prompt text appropriate for the request type
        """

        intent = analyze_user_intent(user_input or "")
        agent_md = get_project_root() / const.AGENTS_MD_FILENAME
        has_agent = all([
            user_input,
            agent_md.exists()
            , agent_md.is_file()
        ])
        if intent == Intent.UNKNOWN or has_agent is False:
            return  CODING_ASSISTANT_SYSTEM_PROMPT
        
        return agent_md.read_text(encoding="UTF-8")        


    def _get_tools(self, user_input: str) -> List:
        """
        Get tools for the current request.

        Currently returns all available tools. Tool selection logic is
        commented out but can be re-enabled in the future.

        Args:
            user_input: User's input text

        Returns:
            List of tool functions available for this request
        """
        if self._cached_tools is None:
            from .agent_repo import load_tools
            self._cached_tools = load_tools()

        return self._cached_tools

    def refine_user_prompt(self, user_input: str) -> str:
        """
        Refine user prompt before sending to LLM.

        For OpenSpec commands, loads and applies the appropriate prompt template.

        Args:
            user_input: Original user input

        Returns:
            Refined prompt, potentially with template applied
        """
        intent = analyze_user_intent(user_input or "")
        refined_prompt = user_input
        prompt_template = None
        if user_input.startswith("/openspec"):
            if any(
                user_input.startswith(prefix)
                for prefix in const.OPENSPEC_PROPOSAL_PREFIXES
            ):
                prompt_template = const.OPENSPEC_PROPOSAL_TEMPLATE
            elif any(
                user_input.startswith(prefix)
                for prefix in const.OPENSPEC_APPLY_PREFIXES
            ):
                prompt_template = const.OPENSPEC_APPLY_TEMPLATE
            elif any(
                user_input.startswith(prefix)
                for prefix in const.OPENSPEC_ARCHIVE_PREFIXES
            ):
                prompt_template = const.OPENSPEC_ARCHIVE_TEMPLATE                
            
            

        if prompt_template:
            prompt_path = get_project_root() / const.PROMPTS_DIR / prompt_template
            if prompt_path.exists() and prompt_path.is_file():
                template_content = prompt_path.read_text(encoding="UTF-8")
                refined_prompt = template_content.replace("$ARGUMENTS", user_input)
                
        return refined_prompt

    def run_workflow(self, user_input: str) -> Optional[str]:
        """
        Run the LLM workflow with the given user input.

        Args:
            user_input: User's input text

        Returns:
            LLM response text, or None if an error occurred
        """
        try:
            resp = self.llm.invoke_chat_stream(
                prompt=self.refine_user_prompt(user_input),
                tools=self._get_tools(user_input),
                include_history=50,
                system_prompt=self.get_system_prompt(user_input),
                max_completion_tokens=self.llm.max_completion_tokens,
            )
            self.console.print()
            self.llm.chat_history.save_history()
            return resp
        except Exception as e:
            logger.exception(e)
            return None

    def display_welcome(self) -> None:
        """Display welcome message and instructions."""
        shell_help.display_welcome(self.console)

    def _show_help(self) -> None:
        """Display comprehensive help information about all available commands."""
        shell_help.display_help(self.console)

    def _show_history(self) -> None:
        """Display recent conversation history."""
        hists = self.llm.chat_history.get_chat_history(40)
        if hists is None or len(hists) == 0:
            self.console.print(const.MSG_NO_HISTORY, style="italic dim")
            return
        for hist in hists:
            self.console.print(hist.get("content", ""))

    def process_command(self, command: str) -> Optional[bool]:
        """
        Process special shell commands.

        Handles commands like:
        - System commands (!command)
        - Exit commands (exit, quit, q, bye)
        - Clear screen
        - Help
        - History management
        - MCP status
        - Ask AI analysis

        Args:
            command: Command string to process

        Returns:
            True if command was handled and shell should continue,
            False if shell should exit,
            None if command was not recognized
        """
        command_lower = command.lower().strip()

        # System command execution
        if command_lower.startswith("!"):
            system_command = command[1:]
            
            # Capture both stdout and stderr for better analysis
            try:
                status, stdout_output, stderr_output = execute_command_realtime_threaded(system_command, timeout=180)
                
                if status == 0:
                    self.cliconsole.print(f"Command executed successfully", color="green")
                else:
                    self.cliconsole.print(f"Command failed with exit code {status}", color="red")
                
                
                self.last_command_output = {
                    "stdout": stdout_output,
                    "stderr": stderr_output,
                    "exit_code": status
                }
                
            except Exception as e:
                self.cliconsole.print(f"Error executing command: {str(e)}", color="red")
                self.last_command_output = f"Error executing command: {str(e)}"
            
            return True

        # Exit commands
        if command_lower in const.EXIT_COMMANDS:
            self.console.print(const.MSG_GOODBYE)
            return False

        # Clear screen
        if command_lower == "clear":
            os.system("clear" if os.name == "posix" else "cls")
            self.display_welcome()
            return True

        # Help
        if command_lower in const.HELP_COMMANDS:
            self._show_help()
            return True

        # History management
        if const.PATTERN_CLEAR_HISTORY.search(
            command_lower
        ) or const.PATTERN_NEW_CHAT.search(command_lower):
            self.llm.chat_history.clear_history()
            return True

        if const.PATTERN_SAVE_HISTORY.search(command_lower):
            self.llm.chat_history.save_history()
            return True

        if const.PATTERN_SHOW_HISTORY.search(command_lower):
            self._show_history()
            return True

        # MCP status (placeholder)
        if const.PATTERN_MCP_STATUS.search(command_lower):
            return True
            
        # Ask AI command
        if const.PATTERN_ASK_AI.search(command_lower) or const.PATTERN_ANALYZE.search(command_lower):
            if self.last_command_output is None:
                self.cliconsole.print("No command output available for analysis.", color="yellow")
                return True            
            # Prepare prompt with captured output
            analysis_prompt = f"Analyze the following shell command output:\n\n{json.dumps(self.last_command_output, indent=2)}\n\nProvide insights and next steps."            
            # Call LLM analysis using existing workflow
            response = self.run_workflow(analysis_prompt)
            if response:
                self.console.print(Panel(Markdown(response), title="AI Analysis"))
            return True

        return None

    def run(self) -> None:
        """
        Main loop for the interactive shell.

        Displays welcome message, then enters a loop that:
        1. Gets user input
        2. Processes commands or sends to LLM
        3. Displays responses
        4. Handles errors gracefully
        """
        self.display_welcome()
        while True:
            try:
                # Get user input with multi-line support and Ctrl+Shift+C cancellation
                user_input = self.cliconsole.get_multiline_input()

                if user_input is None:
                    continue

                # Check for special commands
                command_result = self.process_command(user_input)
                if command_result is not None:
                    if not command_result:
                        break
                    continue

                
                response = self.run_workflow(user_input)

                if not response:
                    self.cliconsole.print(
                        const.MSG_NO_RESPONSE, color="red", end="\n\n"
                    )
                    self.cliconsole.print(user_input, color="red", end="\n\n")
                    continue
                else:
                    self.console.print(
                        Panel(Markdown(response), title=f"Agent Response - Model: {self.llm.response_model}")
                    )

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully - this is where we'll add cancellation logic
                self.cliconsole.print(const.MSG_USE_EXIT, color="yellow")
            except Exception as e:
                self.cliconsole.print(f"Error: {str(e)}", color="red")


@click.command()
@click.option(
    "--config",
    "-c",
    "config_path",
    type=click.Path(exists=True),
    default=None,
    help="Path to Kara Code configuration file.",
)
def code_shell(config_path: Optional[str] = None) -> None:
    """Start an interactive LLM GenAI shell."""
    shell = AgenticShell(config_path)
    shell.run()


if __name__ == "__main__":
    code_shell()