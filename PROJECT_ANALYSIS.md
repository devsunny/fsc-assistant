# FSC Assistant - Project Analysis

## Project Overview

**FSC Assistant** (Fully Self-Coding Assistant) is a command-line tool that leverages Large Language Models to help build software with ease. It provides an interactive shell for AI-assisted coding, document analysis, web scraping, and integration with external services.

## Architecture

### Core Components

```
src/assistant/
├── agents/                    # AI Agent implementations
│   ├── shell.py              # Interactive shell (main entry point)
│   ├── agent_repo.py         # Tool repository with lazy loading
│   ├── tools/                # Core tool implementations
│   ├── web/                  # Web scraping and search tools
│   └── integrations/         # External service integrations
├── cli.py                    # CLI with lazy loading
├── config/                   # Configuration management
├── llm/                      # LLM client and orchestration
├── mcp/                      # Model Context Protocol
└── utils/                    # Utility functions
```

### Key Features

#### 1. Interactive Shell (`agents/shell.py`)
- Multi-line input support
- Command history management
- Rich console output with Markdown rendering
- Model switching at runtime
- Special commands (`!system`, `clear`, `history`, etc.)

#### 2. Tool System (`agents/tools/`)
- **File Operations**: Read/write text/binary files, list projects
- **System Operations**: Execute shell commands, get current time
- **Web Tools**: Fetch webpages, take screenshots, download files
- **Document Analysis**: Extract and analyze content from various file types

#### 3. Web Scraping (`agents/web/`)
- **Webpage Fetching**: Extract content from URLs
- **Screenshots**: Capture webpage screenshots using Playwright
- **Google Search**: Custom search API integration
- **File Downloads**: Download files from URLs

#### 4. Integrations (`agents/integrations/`)
- **JIRA**: Create issues, update status, add comments
- **GitHub**: Create pull requests
- **Lazy Loading**: All integrations load only when used

#### 5. Configuration (`config/`)
- TOML-based configuration
- Environment variable support
- Multiple LLM provider support (OpenAI, Anthropic, etc.)

#### 6. LLM Orchestration (`llm/`)
- Multi-provider support
- Streaming responses
- Conversation history management
- Tool/function calling

## Performance Optimizations

### Startup Time Improvements

**Before Optimization:**
- Total startup: 13.769s
- Import time: 13.569s
- Google API import: 8.7s
- File operations: 9.8s

**After Optimization:**
- Total startup: 0.920s (93% improvement)
- Import time: 0.731s
- Google API import: 0s (deferred)
- File operations: 0.452s (52% reduction)

### Optimization Techniques Applied

1. **Lazy Loading**: Heavy modules (Google API, Jira, GitHub) load only when used
2. **Explicit Imports**: Replaced star imports with explicit imports
3. **Deferred Initialization**: Delay expensive operations until needed
4. **Caching**: Tool lists cached after first access

## Tool Inventory

### Core Tools (17 total)

#### File System Tools
- `save_text_file_to_disk` - Save text files
- `load_text_file_from_disk` - Load text files
- `save_binary_file_to_disk` - Save binary files
- `load_image_files_from_disk` - Load images
- `list_files_in_current_project` - List project files
- `get_current_project_root_folder` - Get project root

#### System Tools
- `run_shell_command` - Execute shell commands
- `get_current_local_time` - Get current time

#### Web Tools
- `fetch_webpage_content` - Extract webpage content
- `capture_web_page_screenshot` - Take screenshots
- `download_web_file_from_url` - Download files
- `search_google_custom_api` - Google search

#### Integration Tools
- `get_jira_issue` - Get JIRA issue details
- `update_jira_issue_status` - Update JIRA status
- `add_jira_comment` - Add JIRA comment
- `create_jira_issue` - Create JIRA issue
- `create_github_pull_request` - Create GitHub PR

## Configuration

### Configuration File (`.fsc-assistant.env.toml`)

```toml
[llm]
default_model = "claude-3-5-sonnet-20241022"
max_completion_tokens = 8192

[llm.anthropic]
api_key = "your-anthropic-api-key"

[llm.openai]
api_key = "your-openai-api-key"

[google]
api_key = "your-google-api-key"
search_engine_id = "your-search-engine-id"

[jira]
server = "https://your-domain.atlassian.net"
username = "your-email@example.com"
api_token = "your-jira-api-token"

[github]
token = "your-github-token"
```

### Environment Variables

- `FSC_ASSISTANT_CONFIG` - Path to config file
- `ANTHROPIC_API_KEY` - Anthropic API key
- `OPENAI_API_KEY` - OpenAI API key
- `DEBUG` - Enable debug mode (true/false)

## Usage Examples

### Interactive Shell

```bash
# Start the interactive shell
fsc-assistant shell

# Or use the Python module
python -m assistant.agents.shell
```

### Special Commands

```
!command    - Execute system command
exit/quit  - Exit the shell
clear      - Clear screen
history    - Show conversation history
model      - Show current model
```

### Document Analysis

```
Explain src/assistant/agents/shell.py
Summarize docs/proposals/
Analyze the project structure
```

### Web Operations

```
Fetch https://example.com and extract the main content
Take a screenshot of https://example.com
Search Google for "Python performance optimization"
```

### Integration Examples

```
Create a JIRA issue in project PROJ with title "Bug fix needed"
Update JIRA issue PROJ-123 to status "In Progress"
Create a GitHub PR from branch feature-branch to main
```

## Dependencies

### Core Dependencies
- `click` - CLI framework
- `rich` - Rich text and beautiful formatting
- `pydantic` - Data validation
- `toml` - Configuration parsing

### LLM Providers
- `anthropic` - Anthropic Claude
- `openai` - OpenAI GPT models

### Optional Dependencies
- `playwright` - Web scraping and screenshots
- `google-api-python-client` - Google search
- `atlassian-python-api` - JIRA integration
- `PyGithub` - GitHub integration

### Development Dependencies
- `pytest` - Testing framework
- `black` - Code formatting
- `mypy` - Type checking

## Installation

### From Source

```bash
git clone <repository-url>
cd fsc-assistant
pip install -e .
```

### With Optional Dependencies

```bash
# Web scraping support
pip install 'fsc-assistant[web]'
playwright install chromium

# All optional dependencies
pip install 'fsc-assistant[all]'
```

## Testing

```bash
# Run tests
pytest

# Test startup time
python verify_optimizations.py

# Performance analysis
python analyze_performance.py
```

## Project Structure

```
fsc-assistant/
├── src/assistant/              # Main package
│   ├── agents/                 # AI agents and tools
│   ├── cli.py                  # CLI entry point
│   ├── config/                 # Configuration
│   ├── llm/                    # LLM orchestration
│   ├── mcp/                    # Model Context Protocol
│   └── utils/                  # Utilities
├── docs/                       # Documentation
│   └── proposals/              # Architecture proposals
├── tests/                      # Test suite
├── pyproject.toml              # Project configuration
└── README.md                   # Main documentation
```

## Recent Improvements

### Performance Optimizations (v0.1.0)
- Reduced startup time by 93% (13.7s → 0.92s)
- Implemented lazy loading for heavy dependencies
- Optimized import patterns
- Reduced file system operations by 52%

### New Features
- Google Custom Search API integration
- Enhanced document analysis capabilities
- Improved error handling and user feedback
- Rich console output with Markdown support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

[License information to be added]

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the documentation in `docs/`
- Review the examples in this README

---

*Last updated: 2024*
*Version: 0.1.0*
