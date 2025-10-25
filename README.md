# FSC Assistant

## Overview
The Fully Self-Coding (FSC) Assistant is a command-line tool designed to leverage Large Language Model's coding capability to help build software with ease.

## Directory Structure
```
fsc-assistant/src/
├── fsc
│   ├── __init__.py
│   ├── __pycache__
│   ├── assistant_shell.py
│   ├── cli.py
│   ├── commands
│   ├── config.py
│   ├── llm
│   ├── tools
│   └── utils

```

### Key Components
- **`assistant_shell.py`**: Core logic for the assistant's interaction.
- **`cli.py`**: Command-line interface implementation.
- **`commands/`**: Handling of specific commands and their execution.
- **`config.py`**: Configuration management for the system.
- **`llm/`**: Integration with LLM models (e.g., switching between models).
- **`tools/`**: Tools for image processing, real-time command execution, and more.
- **`utils/`**: Utility functions for prompt handling and other tasks.

## Installation
1. **pip installation**
```bash
   pip install fsc-assistant
```
2. **source installation**
```bash
git clone git@github.com:devsunny/fsc-assistant.git
pip install -e fsc-assistant
```

## Usage Example
1. **Start the Assistant**:
   ```bash
   fsc --help
   fsc config set -g "llm.base_url" "<your_llm_api_base_url>"
   fsc config set -g "llm.api_key" "<your_llm_api_api_key>"
   fsc config set -g "llm.models" '["gpt-5", "claude.sonnet-4-5", "gpt-4o"]'
   fsc shell
   ```
   or

   ```bash
   python -m fsc.cli
   ```


## Architecture Design
The system is designed with modularity in mind, allowing easy integration of new tools and models. Key design patterns include:
- **Separation of concerns**: Different modules handle specific tasks (e.g., commands vs. LLM).
- **Extensibility**: Adding new functions or models through the `tools/` directory.
- **Configurable settings**: Using `config.py` to adjust system behavior.

## Next Steps
Update this README to reflect any new features or changes in the codebase.