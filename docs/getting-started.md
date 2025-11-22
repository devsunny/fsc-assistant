# Getting Started Guide

Welcome to FSC Assistant! This guide will help you get up and running in just 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for installation from source)

## Installation

### Option 1: From Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/fsc-assistant.git
cd fsc-assistant

# Install in development mode
pip install -e .

# Install with web scraping support (recommended)
pip install 'fsc-assistant[web]'
playwright install chromium
```

### Option 2: Quick Install

```bash
# Install directly from repository
pip install git+https://github.com/yourusername/fsc-assistant.git

# Install with all optional dependencies
pip install 'fsc-assistant[all]'
```

## Configuration

### Step 1: Create Configuration File

Create a file named `.fsc-assistant.env.toml` in your home directory:

```bash
# Create config file in your home directory
touch ~/.fsc-assistant.env.toml
```

### Step 2: Add API Keys

Edit the configuration file and add your API keys:

```toml
[llm]
default_model = "claude-3-5-sonnet-20241022"
max_completion_tokens = 8192

[llm.anthropic]
api_key = "sk-ant-your-anthropic-api-key-here"

# Optional: Add OpenAI as fallback
[llm.openai]
api_key = "sk-your-openai-api-key-here"
```

### Step 3: Configure Optional Services (Optional)

Add configurations for additional services:

```toml
[google]
api_key = "your-google-api-key"
search_engine_id = "your-search-engine-id"

[jira]
server = "https://your-domain.atlassian.net"
username = "your-email@example.com"
api_token = "your-jira-api-token"

[github]
token = "ghp_your_github_token_here"
```

## First Run

### Start the Interactive Shell

```bash
# Method 1: Using the installed command
fsc-assistant shell

# Method 2: Using Python module
python -m assistant.agents.shell

# Method 3: Direct script execution
python src/assistant/agents/shell.py
```

### Your First Conversation

Once the shell starts, you'll see a welcome message. Try these commands:

```
# Get help
help

# Check current model
model

# Ask a simple question
What can you help me with?

# Analyze a file (if you're in the project directory)
Explain how the shell.py file works

# Try a system command
!pwd
!ls -la
```

## Basic Usage Examples

### 1. Code Analysis

```
Analyze the src/assistant/agents/shell.py file and explain its main components
```

### 2. Document Summarization

```
Summarize the docs/proposals/001-rename-builtin-to-core-tools.md file
```

### 3. Web Operations

```
Fetch https://example.com and extract the main content
```

### 4. System Commands

```
!git status
!find . -name "*.py" | head -10
```

### 5. Project Analysis

```
List all Python files in the project and give me an overview of the codebase structure
```

## Understanding the Output

The assistant provides rich, formatted output:

- **Green text**: Assistant responses and success messages
- **Red text**: Error messages
- **Yellow text**: Warnings and information
- **Panels**: Formatted responses with titles
- **Markdown**: Rendered Markdown for better readability

## Special Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!command` | Execute system command | `!ls -la` |
| `exit/quit/q/bye` | Exit the shell | `exit` |
| `clear` | Clear screen | `clear` |
| `history` | Show conversation history | `history` |
| `model` | Show current model | `model` |

## Next Steps

Now that you're familiar with the basics, explore:

1. **[Shell Guide](shell-guide.md)** - Master the interactive shell
2. **[Tools Guide](tools-guide.md)** - Learn about all available tools
3. **[Configuration Guide](configuration.md)** - Customize your setup
4. **[Examples](examples/)** - See more usage examples

## Troubleshooting

### "Command not found" error

```bash
# Make sure the package is installed
pip show fsc-assistant

# If not, reinstall
pip install -e .
```

### "API key not found" error

```bash
# Check if config file exists
ls -la ~/.fsc-assistant.env.toml

# Verify API key is correct
cat ~/.fsc-assistant.env.toml
```

### Slow startup

```bash
# Check Python version
python --version  # Should be 3.8+

# Verify installation
python -c "from assistant.agents.shell import AgenticShell; print('OK')"
```

### Web scraping not working

```bash
# Install web dependencies
pip install 'fsc-assistant[web]'
playwright install chromium
```

## Getting Help

- 📖 Check the [full documentation](README.md)
- 🔍 Search [existing issues](https://github.com/yourusername/fsc-assistant/issues)
- 💬 Start a [discussion](https://github.com/yourusername/fsc-assistant/discussions)
- 🐛 Report a [bug](https://github.com/yourusername/fsc-assistant/issues/new)

## Tips for Success

1. **Start Simple**: Begin with basic questions before complex tasks
2. **Be Specific**: Provide clear, detailed prompts for better results
3. **Use System Commands**: Leverage `!command` for system operations
4. **Check History**: Use `history` to review past conversations
5. **Experiment**: Try different tools and see what works best

---

**Congratulations!** You're now ready to use FSC Assistant. Happy coding! 🤖✨

*Need more help? Check out our [Shell Guide](shell-guide.md) for detailed usage instructions.*