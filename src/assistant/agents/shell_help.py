"""
Help system for the Kara Code shell.

This module contains all help text and welcome messages displayed to users.
"""

from rich.console import Console
from rich.markdown import Markdown

# Welcome message displayed when shell starts
WELCOME_TEXT = """**Welcome to the Full self-coding Assistant shell!**
### Commands:
- Type your prompt and press Enter twice to submit
- Type 'exit' or 'quit' or 'bye' to leave
- Type 'clear' to clear CLI console screen
- Type 'clear history', 'save history', 'show history' to view, save and clear history
- Type 'help' to see all available commands
- Press Ctrl+C to cancel current input

### Multi-line Input:
Enter your prompt. Press Enter twice (empty line) to submit.
"""

# Comprehensive help text
HELP_TEXT = """
# Full self-coding Assistant- Command Reference

## 🎯 General Commands

### **help**
Display this help message showing all available commands and their descriptions.

**Usage:** `help`

---

### **exit** | **quit** | **q** | **bye**
Exit the Kara Code shell and disconnect from all services.

**Usage:** `exit`

---

### **clear**
Clear the console screen and redisplay the welcome message.

**Usage:** `clear`

---

## 💬 Chat History Management

### **show history**
Display the last 40 messages from your conversation history.

**Usage:** `show history`

---

### **save history**
Manually save the current conversation history to disk.

**Usage:** `save history`

**Note:** History is automatically saved after each interaction.

---

### **clear history** | **new chat**
Clear the current conversation history and start a fresh session.

**Usage:** `clear history` or `new chat`

---

## 🔧 System Commands

### **!<command>**
Execute a shell command directly from the Kara Code shell.

**Usage:** `!ls -la` or `!git status`

**Examples:**
- `!pwd` - Show current directory
- `!git log --oneline -5` - Show last 5 git commits
- `!python --version` - Check Python version

---

## 🔌 MCP (Model Context Protocol) Commands

### **mcp status**
Display the status of all configured MCP servers, including connection state and available tools.

**Usage:** `mcp status`

**Output includes:**
- Server name and transport type
- Connection status (connected / disconnected)
- Server description
- Number of available tools

---

## 🤖 Model Management

### **Switch Model** (via AI)
You can ask the AI to switch to a different LLM model during your session.

**Usage:** Ask naturally, e.g., "switch to gpt-4" or "use claude-3-opus"

**Available models:** Depends on your configuration in `kara.toml`

---

### **Show Current Model** (via AI)
Ask the AI which model is currently active.

**Usage:** "what model are you using?" or "show current model"

---

## 📝 OpenSpec Commands

### **/openspec-proposal** | **/openspec:proposal**
Create a new OpenSpec proposal for a feature or change.

**Usage:** `/openspec-proposal <description>`

**Example:** `/openspec-proposal add user authentication with OAuth2`

---

### **/openspec-apply** | **/openspec:apply**
Apply an approved OpenSpec proposal to the codebase.

**Usage:** `/openspec-apply <proposal-id>`

---

### **/openspec-archive** | **/openspec:archive**
Archive a completed or rejected OpenSpec proposal.

**Usage:** `/openspec-archive <proposal-id>`

---

## 📄 Document Analysis

The shell automatically detects document analysis requests when you mention file extensions like `.pdf`, `.docx`, `.xlsx`, etc., combined with keywords like "explain", "summarize", "describe", or "extract".

**Supported formats:**
- PDF (.pdf)
- Word (.docx, .doc)
- Excel (.xlsx, .csv)
- PowerPoint (.pptx)
- Images (.jpg, .png, .jpeg, .tiff, .bmp)

**Examples:**
- "Summarize the contents of report.pdf"
- "Extract tables from data.xlsx"
- "Explain what's in diagram.png"

---

## 💡 Tips & Tricks

1. **Multi-line input:** Press Enter twice (empty line) to submit your prompt
2. **Interrupt:** Press Ctrl+C to cancel current input without exiting
3. **Context:** The AI maintains conversation history for context-aware responses
4. **Tools:** The AI has access to various tools for file operations, code analysis, and more
5. **Natural language:** You can ask questions naturally; the AI will understand and use appropriate tools

---

## 🛠️ Available AI Tools

The AI assistant has access to numerous tools including:
- File system operations (read, write, list files)
- Code analysis and generation
- Git operations
- JIRA integration
- GitHub integration
- Document processing
- LiteLLM user/team management
- MCP server tools (when connected)

Ask the AI to perform tasks naturally, and it will use the appropriate tools automatically.

---

## 📚 Additional Resources

- Configuration file: `kara.toml`
- MCP registry: `mcp.json`
- Logs: Check console output for detailed information

For more information, visit the project documentation or ask the AI assistant!
"""


def display_welcome(console: Console) -> None:
    """
    Display the welcome message when the shell starts.

    Args:
        console: Rich Console instance for output
    """
    console.print(Markdown(WELCOME_TEXT))


def display_help(console: Console) -> None:
    """
    Display comprehensive help information about all available commands.

    Args:
        console: Rich Console instance for output
    """
    console.print(Markdown(HELP_TEXT))
