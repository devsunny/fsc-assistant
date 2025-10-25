import logging
import os
import re
# LangChain/LangGraph imports
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .config import configman as global_config, ConfigManager
from .utils.prompt_toolkit_console import PromptConsole
from .llm.llm_client import BuiltinToolsLLMClient
from .tools.built_in_tools import BUILTIN_TOOLS as tools, get_project_root_dir
from .tools.realtime_command_executor import execute_system_command_realtime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

         

class AiCodingAssistantShell:
    def __init__(self, config:ConfigManager = None): 
        self.console = Console()            
        self.config = config if config is not None else global_config
        self.base_url = self.config.get("llm.base_url")        
        self.api_key = self.config.get("llm.api_key")       
        self.max_completion_tokens = self.config.get_int("llm.max_completion_tokens", default=32000) 
        models  = self.config.get("llm.models")        
        assert models is not None and len(models)>0, f"please config LLM models in {ConfigManager.CONFIG_FILE}"
        assert self.base_url is not None and len(self.base_url)>0, f"please config LLM base_url in {ConfigManager.CONFIG_FILE}"
        assert self.api_key is not None and len(self.api_key)>0, f"please config LLM api_key in {ConfigManager.CONFIG_FILE}"
        
        self.llm_models = [models] if isinstance(models, str) else models
        self.selected_model = models[0]
        self.prompt_console = PromptConsole()
        self.llm = BuiltinToolsLLMClient(
            model=self.selected_model,  # Use a capable model name the proxy will route
            base_url=self.base_url,
            api_key=self.api_key, 
            stream_handler=lambda x: print(x, end="", flush=True),    
            debug= os.environ.get("DEBUG", "False").lower() == "true"     
        )
        
        
    def _get_tools(self):
        ai_tools = [tool for tool in tools]
        ai_tools.append(self.switch_llm_model)
        ai_tools.append(self.current_model_name)
        return ai_tools

    
    def switch_llm_model(self, model_name:str, permenant:bool=False)-> str:
        """Switch the LLM model used by the assistant"""
        if model_name not in self.llm_models:
            return f"Model {model_name} is not in configured models: {self.llm_models}"             
        self.selected_model = model_name
        self.llm.model = model_name        
        if permenant is True:
            models = [ m for m in self.config.get("llm.models", []) if m != model_name]
            models.insert(0, model_name)
            self.config.set("llm.models", models)
            self.config.save_config()                    
        return f"Switched to model {model_name}"
    
    def current_model_name(self):
        """Get the current LLM model name"""
        return self.selected_model  
    
    def run_workflow(self, user_input):
        try:
            resp = self.llm.invoke_chat_stream(prompt=user_input, tools=self._get_tools(), include_history=50, max_completion_tokens=self.max_completion_tokens)
        # resp = self.llm.invoke_chat(prompt=user_input, tools=tools, include_history=50, max_completion_tokens=self.max_completion_tokens)        
            self.console.print()
            self.llm.chat_history.save_history()
            return resp
        except Exception as e:
            logger.exception(e)
            return None
    
    
    def display_welcome(self):
        """Display welcome message and instructions"""
        welcome_text = """Welcome to the interactive AI coding assistant shell!
### Commands:
- Type your prompt and press Enter twice to submit
- Type 'exit' or 'quit' or 'bye' to leave
- Type 'clear' to clear CLI console screen
- Type 'new chat' or 'new' to start a new chat session
- Type 'clear history', 'save history', 'show history' to view, save and clear history  
- Type '/your_system_command' to run a system command (e.g., /ls -la)
- Type 'help' to display this help message
- Press Ctrl+C to cancel current input
"""
        self.console.print(Markdown(welcome_text))
        
        
    def _show_history(self):
        hists = self.llm.chat_history.get_chat_history(40)
        for hist in hists:
            if hist.get("role") == "user":
                self.console.print(hist.get("content"))
    
    
    def get_system_prompt(self):
        agent_md = get_project_root_dir() / "AGENTS.md"
        if agent_md.exists and agent_md.is_file():
            return agent_md.read_text(encoding="UTF-8")
        else:
            return """> **Role:** You are an expert software engineer and code generation assistant.
> **Goal:** Generate clean, correct, and well-structured code that fulfills user requirements.
> **Capabilities:** You can generate, refactor, document, and explain code across multiple programming languages and frameworks.

#### ✅ **Core Directives**

1. **Correctness First:** Always produce code that runs without syntax errors and follows best practices for the target language.
2. **Clarity & Readability:** Use descriptive variable names, proper indentation, and consistent style conventions.
3. **Explain When Helpful:** Provide short, clear explanations when requested or when the purpose of the code might not be obvious.
4. **Security & Safety:** Never include insecure practices (e.g., hard-coded credentials, unsafe evals, SQL injection vulnerabilities).
5. **Scalability & Maintainability:** Prefer modular, reusable designs with clear separation of concerns.
6. **Precision:** Follow the user’s specification exactly—language, libraries, style, and output format.
7. **Documentation:** When generating larger codebases, include concise comments or docstrings explaining key functions and classes.

#### ⚙️ **Special Instructions**

* If the user does **not** specify a language, ask for clarification before generating.
* If multiple solutions exist, explain trade-offs and recommend one.
* If the user provides a partial snippet, complete it rather than rewriting everything.
* When refactoring, retain all functional behavior unless instructed otherwise.
* Never insert placeholders like “TODO” or “example” without user approval.

#### 💬 **Example Behaviors**

* **User:** “Generate a Python script that reads a CSV and plots a bar chart.”

  * ✅ Output: Working Python script using `pandas` and `matplotlib`, with clear comments and a title on the chart.
* **User:** “Convert this function to JavaScript.”

* ✅ Output: Equivalent, idiomatic JavaScript code with minor adjustments to handle type differences.
        
        """    
    
    def process_command(self, command: str) -> bool:
        """Process special commands"""
        command_lower = command.lower().strip()        
        if command_lower.startswith("/"):
            system_command = command[1:]
            status_code, _ = execute_system_command_realtime(system_command, os.environ)
            if status_code==0:
                self.prompt_console.print("command execute sucessfully", color="green")
            else:
                self.prompt_console.print(f"command execution failed: status code {status_code}", color="red")
            return True
        
        if command_lower in ['exit', 'quit', 'q', "bye"]:
            self.console.print("[bold red]Goodbye![/bold red]")
            return False
            
        if command_lower == 'clear':            
            os.system('clear' if os.name == 'posix' else 'cls')
            self.display_welcome()
            return True                
        
        if re.search(r'^clear\s*history$', command_lower) or re.search(r'new(\s*chat)?$', command_lower):
            self.llm.chat_history.clear_history()            
            return True
        
        if re.search(r'^save\s*history$', command_lower):
            self.llm.chat_history.save_history()            
            return True
        
        if re.search(r'^show\s*history$', command_lower):
            self._show_history() 
            return True
                    
        return None        
        
        
    def run(self):
            """Main loop for the interactive shell"""
            self.display_welcome()
            while True:
                try:
                    # Get user input
                    user_input = self.prompt_console.get_multiline_input()
                    
                    if user_input is None:
                        continue
                        
                    # Check for special commands
                    command_result = self.process_command(user_input)
                    if command_result is not None:
                        if not command_result:
                            break
                        continue
                        
                    # Call LLM API
                    self.prompt_console.print("[Asisstant]: ", color="green",  end="")
                    response = self.run_workflow(user_input)
                    
                    if not response:                    
                        self.prompt_console.print("No response received", color="red", end="")
                        continue
                    else:
                        self.console.print(Panel(Markdown(response), title="Agent Response"))
                        
                        
                except KeyboardInterrupt:
                    self.prompt_console.print("Use 'exit' or 'quit' to leave the shell", color="yellow", end="")                    
                except Exception as e:
                    self.prompt_console.print(f"Error: {str(e)}", color="red", end="")



    
    
if __name__ == "__main__":
    shell = AiCodingAssistantShell()
    shell.run()
   




       

