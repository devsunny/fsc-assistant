# Migration Guide: Python to Node.js Version

This guide helps developers transition from the original Python FSC Assistant to the Node.js implementation.

## Overview

The Node.js version maintains feature parity with the Python version while providing:
- Improved performance and memory usage
- Better cross-platform compatibility  
- Enhanced TypeScript support for better development experience
- Modern module system and dependency management

## Key Differences

### 1. Installation Method
**Python Version:**
```bash
pip install fsc-assistant
```

**Node.js Version:**
```bash
# Install from npm (recommended)
npm install -g fsc-assistant

# Or install locally in project
npm install fsc-assistant

# Or clone and build from source
git clone <repository>
cd fsc-assistant-nodejs
npm install
npm run build
```

### 2. Configuration Format
**Python Version:** JSON/YAML configuration files  
**Node.js Version:** TOML configuration files

#### Python Config (JSON):
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4"
  },
  "jira": {
    "base_url": "https://your-domain.atlassian.net",
    "token": "your-jira-token"
  }
}
```

#### Node.js Config (TOML):
```toml
[llm]
provider = "openai"
model = "gpt-4"

[jira]
base_url = "https://your-domain.atlassian.net"
token = "your-jira-token"
```

### 3. Environment Variables
**Python Version:**
```
LLM_API_KEY=your-key
JIRA_TOKEN=your-token
GITHUB_TOKEN=your-token
```

**Node.js Version:**
```
FSC_LLM_API_KEY=your-key
FSC_JIRA_TOKEN=your-token  
FSC_GITHUB_TOKEN=your-token
```

### 4. Command Line Interface
**Python Version:**
```bash
fsc --help
fsc --config config.json
```

**Node.js Version:**
```bash
fsc --help
fsc --config ~/.fsc-assistant.env.toml
```

## Tool Migration

### File System Tools
| Python | Node.js |
|--------|---------|
| `save_text_file` | `save_text_file` |
| `load_text_file` | `load_text_file` |
| `list_files` | `list_files` |

### Web Scraping Tools  
| Python | Node.js |
|--------|---------|
| `fetch_webpage` | `fetch_web_page` |
| `capture_screenshot` | `capture_web_page_screenshot` |
| `download_file` | `download_web_file_from_url` |

### Search Tools
| Python | Node.js |
|--------|---------|
| `google_search` | `google_search` |
| `web_search` | `search_web` |

### JIRA Integration
| Python | Node.js |
|--------|---------|
| `create_jira_issue` | `create_jira_issue` |
| `get_jira_issue` | `get_jira_issue` |
| `search_jira_issues` | `search_jira_issues` |

### GitHub Integration
| Python | Node.js |
|--------|---------|
| `create_github_issue` | `create_github_issue` |
| `get_github_issue` | `get_github_issue` |
| `search_github_issues` | `search_github_issues` |

## Configuration Migration

### 1. Convert Configuration Files
Convert your existing JSON/YAML config to TOML format:

**Before (Python - JSON):**
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "sk-..."
  },
  "jira": {
    "base_url": "https://your-domain.atlassian.net",
    "token": "jira-token-here"
  }
}
```

**After (Node.js - TOML):**
```toml
[llm]
provider = "openai"
model = "gpt-4"
api_key = "sk-..."

[jira]
base_url = "https://your-domain.atlassian.net"
token = "jira-token-here"
```

### 2. Update Environment Variables
Rename your environment variables to use the `FSC_` prefix:

**Before:**
```bash
export LLM_API_KEY=sk-...
export JIRA_TOKEN=jira-token-here
export GITHUB_TOKEN=github-token-here
```

**After:**
```bash
export FSC_LLM_API_KEY=sk-...
export FSC_JIRA_TOKEN=jira-token-here  
export FSC_GITHUB_TOKEN=github-token-here
```

## Code Migration for Developers

### 1. Import Statements
**Python Version:**
```python
from fsc_assistant.tools import save_text_file, load_text_file
```

**Node.js Version:**
```javascript
const { saveTextFile, loadTextFile } = require('./src/agents/tools/file_system');
```

### 2. Function Calls
The function signatures remain largely the same, but with JavaScript/TypeScript conventions:

**Python Version:**
```python
result = save_text_file('file.txt', 'content')
```

**Node.js Version:**
```javascript
const result = await saveTextFile('file.txt', 'content');
```

### 3. Error Handling
The Node.js version uses JavaScript/TypeScript promises and async/await:

**Python Version:**
```python
try:
    result = some_function()
except Exception as e:
    print(f"Error: {e}")
```

**Node.js Version:**
```javascript
try {
    const result = await someFunction();
} catch (error) {
    console.error(`Error: ${error}`);
}
```

## Performance Considerations

### 1. Memory Usage
The Node.js version typically uses less memory than the Python version due to:
- More efficient garbage collection in V8 engine
- Better handling of asynchronous operations
- Optimized string and object management

### 2. Startup Time
Node.js version has faster startup times because:
- No Python interpreter overhead
- Direct compilation to JavaScript
- Faster module loading

## Testing Migration

Before migrating, run all existing tests to ensure functionality:

```bash
# Test the Node.js version
npm test

# Run specific test suites
npm run test:unit
npm run test:integration  
npm run test:performance
```

## Common Issues and Solutions

### 1. Missing Dependencies
If you encounter dependency issues:
```bash
npm install
# or
npm ci
```

### 2. Configuration File Not Found
Ensure your configuration file is in the correct location:
- Default: `~/.fsc-assistant.env.toml`
- Custom path: Use `--config` flag

### 3. API Key Issues  
Make sure environment variables are properly set with `FSC_` prefix.

## Best Practices for Node.js Version

1. **Use TypeScript**: Take advantage of type safety
2. **Leverage Async/Await**: For better asynchronous code handling
3. **Modular Design**: Use ES6 modules or CommonJS as appropriate
4. **Error Handling**: Implement proper try/catch blocks
5. **Environment Variables**: Use the `FSC_` prefix for configuration

## Support and Feedback

If you encounter issues during migration:
1. Check the documentation in this repository
2. Open an issue on GitHub with details about your problem
3. Contact the development team for assistance

The Node.js version maintains full backward compatibility with existing workflows while providing enhanced performance and developer experience.