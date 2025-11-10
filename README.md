# FSC Assistant

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/yourusername/fsc-assistant)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Overview

**FSC Assistant** (Fully Self-Coding Assistant) is a powerful command-line tool that leverages Large Language Models to help you build software with ease. It provides an interactive AI-powered shell for coding assistance, document analysis, web scraping, and seamless integration with external services like JIRA and GitHub.

### Key Features

- 🤖 **Interactive AI Shell** - Chat with LLMs in a rich terminal interface
- 📁 **File Operations** - Read, write, and analyze files and projects
- 🌐 **Web Scraping** - Fetch webpages, take screenshots, search Google
- 🔗 **Service Integrations** - JIRA and GitHub integration
- ⚡ **Blazing Fast** - Optimized startup (0.92s, 93% faster than v0.0.1)
- 🛠️ **Developer Tools** - Execute shell commands, manage conversation history
- 🎨 **Rich Output** - Beautiful Markdown rendering in the terminal

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/devsunny/fsc-assistant.git
cd fsc-assistant

# Install in development mode
pip install -e .

# Install with optional dependencies (recommended)
pip install 'fsc-assistant[web]'
playwright install chromium
```

### Configuration

Create a configuration file at `~/.fsc-assistant.env.toml`:

```toml
[llm]
default_model = "claude-3-5-sonnet-20241022"
max_completion_tokens = 8192
provider = "anthropic"

[anthropic]
api_key = "your-anthropic-api-key"
base_url = 


[openai]
api_key = "your-openai-api-key"
base_url = 
```

### Basic Usage

```bash
# Start the interactive shell
fsc-assistant shell

# Or use Python module
python -m assistant.agents.shell
```

## Usage Examples

### Interactive Shell

Once in the shell, you can:

```
# Ask about your code
Explain how the shell.py file works

# Analyze documents
Summarize the docs/proposals/ directory

# Execute system commands
!ls -la
!git status

# Web operations


# Integration with external services
Create a JIRA issue in project PROJ with title "Bug fix needed"
Create a GitHub PR from branch feature-branch to main

# Manage conversation
history          # Show conversation history
clear            # Clear screen
exit             # Exit shell
```

### Special Commands

| Command | Description |
|---------|-------------|
| `!command` | Execute system command |
| `exit/quit/q/bye` | Exit the shell |
| `clear` | Clear the screen |
| `history` | Show conversation history |
| `model` | Show current LLM model |

## Architecture

### Core Components

```
src/assistant/
├── agents/           # AI Agent implementations
│   ├── shell.py     # Interactive shell (main entry)
│   ├── agent_repo.py # Tool repository (lazy loaded)
│   ├── tools/       # Core tools (file, system, time)
│   ├── web/         # Web scraping tools
│   └── integrations/ # JIRA, GitHub integrations
├── cli.py           # CLI entry point
├── config/          # Configuration management
├── llm/            # LLM orchestration
└── utils/          # Utility functions
```

### Performance Optimized

The assistant is highly optimized for fast startup:

- **Lazy Loading**: Heavy modules (Google API, JIRA, GitHub) load only when used
- **Smart Imports**: Explicit imports avoid unnecessary loading
- **Caching**: Tool lists and configurations cached after first access

**Performance Metrics:**
- Startup time: **0.92s** (93% improvement from v0.0.1)
- Memory footprint: Minimal (only load what's needed)
- File operations: 52% reduction in system calls

## Tool Reference

### File System Tools

| Tool | Description |
|------|-------------|
| `save_text_file_to_disk` | Save text content to a file |
| `load_text_file_from_disk` | Load text content from a file |
| `save_binary_file_to_disk` | Save binary content to a file |
| `load_image_files_from_disk` | Load image files |
| `list_files_in_current_project` | List all files in project |
| `get_current_project_root_folder` | Get project root directory |

### System Tools

| Tool | Description |
|------|-------------|
| `run_shell_command` | Execute shell commands interactively |
| `get_current_local_time` | Get current local time with timezone |

### Web Tools

| Tool | Description |
|------|-------------|
| `fetch_webpage_content` | Extract content from webpages |
| `capture_web_page_screenshot` | Take screenshots of webpages |
| `download_web_file_from_url` | Download files from URLs |
| `search_google_custom_api` | Search Google with custom API |

### Integration Tools

| Tool | Description |
|------|-------------|
| `get_jira_issue` | Get JIRA issue details |
| `update_jira_issue_status` | Update JIRA issue status |
| `add_jira_comment` | Add comment to JIRA issue |
| `create_jira_issue` | Create new JIRA issue |
| `create_github_pull_request` | Create GitHub pull request |

## Configuration

### Configuration File

The assistant uses a TOML configuration file (`.fsc-assistant.env.toml`):

```toml
[llm]
default_model = "claude-3-5-sonnet-20241022"
max_completion_tokens = 8192
temperature = 0.7

[llm.anthropic]
api_key = "sk-ant-..."

[llm.openai]
api_key = "sk-..."

[google]
api_key = "your-google-api-key"
search_engine_id = "your-search-engine-id"

[jira]
server = "https://your-domain.atlassian.net"
username = "your-email@example.com"
api_token = "your-jira-api-token"

[github]
token = "ghp_..."
```

### Environment Variables

- `FSC_ASSISTANT_CONFIG` - Path to custom config file
- `ANTHROPIC_API_KEY` - Anthropic API key
- `OPENAI_API_KEY` - OpenAI API key
- `DEBUG` - Enable debug mode (true/false)

## Installation Options

### Minimal Installation

```bash
pip install -e .
```

### With Web Scraping

```bash
pip install 'fsc-assistant[web]'
playwright install chromium
```

### Full Installation

```bash
pip install 'fsc-assistant[all]'
playwright install chromium
```

### Development Installation

```bash
git clone https://github.com/yourusername/fsc-assistant.git
cd fsc-assistant
pip install -e ".[dev]"
```

## Development

### Project Structure

```
fsc-assistant/
├── src/assistant/          # Main package
│   ├── agents/            # AI agents and tools
│   ├── cli.py             # CLI entry point
│   ├── config/            # Configuration
│   ├── llm/              # LLM orchestration
│   ├── mcp/              # Model Context Protocol
│   └── utils/            # Utilities
├── docs/                  # Documentation
│   └── proposals/        # Architecture proposals
├── tests/                # Test suite
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/assistant

# Test startup performance
python verify_optimizations.py

# Performance analysis
python analyze_performance.py
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
flake8 src/
```

## Recent Updates

### v0.1.0 (Current)

#### Performance Improvements
- ⚡ **93% faster startup** (13.7s → 0.92s)
- 🚀 Lazy loading for heavy dependencies
- 📉 52% reduction in file system operations
- 🎯 Optimized import patterns

#### New Features
- 🔍 Google Custom Search API integration
- 📄 Enhanced document analysis
- 🎨 Rich Markdown output in terminal
- 🛡️ Improved error handling

#### Bug Fixes
- Fixed import loops and circular dependencies
- Improved error messages for missing dependencies
- Better handling of missing configuration

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Submit a pull request

## Roadmap

### Planned Features

- [ ] **Plugin System** - Extensible tool architecture
- [ ] **More LLM Providers** - Gemini, Llama, etc.
- [ ] **Database Integration** - PostgreSQL, MySQL support
- [ ] **Advanced Web Scraping** - JavaScript rendering, forms
- [ ] **Team Collaboration** - Shared configurations and history
- [ ] **IDE Integration** - VS Code extension
- [ ] **Cloud Storage** - S3, GCS, Azure integration

### Long-term Vision

- **AI-Powered Development** - End-to-end software development assistance
- **Multi-modal Support** - Image and code analysis
- **Project Generation** - Scaffold entire projects from descriptions
- **Smart Refactoring** - AI-assisted code refactoring
- **Documentation Generation** - Auto-generate docs from code

## Troubleshooting

### Common Issues

#### Slow Startup

If startup is slow (>2s), check:
- Are you using the latest version? (`pip install -U fsc-assistant`)
- Is lazy loading working? (`python -c "from assistant.agents.shell import AgenticShell; print('OK')"`)
- Are there unnecessary imports in your config?

#### Missing Dependencies

```bash
# Install missing web dependencies
pip install 'fsc-assistant[web]'
playwright install chromium

# Install all optional dependencies
pip install 'fsc-assistant[all]'
```

#### Configuration Issues

```bash
# Check config file location
echo $FSC_ASSISTANT_CONFIG

# Validate config syntax
python -c "import toml; toml.load('.fsc-assistant.env.toml')"
```

### Getting Help

- 📖 Check the [documentation](docs/)
- 🔍 Search [existing issues](https://github.com/yourusername/fsc-assistant/issues)
- 💬 Start a [discussion](https://github.com/yourusername/fsc-assistant/discussions)
- 🐛 Report a [bug](https://github.com/yourusername/fsc-assistant/issues/new)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Inspired by the need for better AI-assisted development tools
- Built with amazing open-source libraries and tools

---

**Happy Coding!** 🤖✨

*For more information, check out our [documentation](docs/) and [examples](examples/).*
