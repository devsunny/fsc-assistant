# Configuration Guide for FSC Assistant

This document explains how to configure the FSC Assistant Node.js implementation and highlights any differences from the Python version.

## Configuration Methods

The assistant supports multiple configuration methods in order of precedence:

1. **Environment Variables** (highest priority)
2. **Configuration Files** 
3. **Command Line Options**
4. **Default Values** (lowest priority)

## Configuration File Format

### TOML Format
The Node.js version uses TOML for configuration files, which is different from the Python version's JSON/YAML format.

Example `~/.fsc-assistant.env.toml`:
```toml
[llm]
provider = "openai"
model = "gpt-4"
api_key = "your-api-key-here"
temperature = 0.7
max_tokens = 1000

[jira]
base_url = "https://your-domain.atlassian.net"
token = "your-jira-token"

[github]
token = "your-github-token"

[logging]
level = "info"
file = "/var/log/fsc-assistant.log"
```

## Key Configuration Differences from Python Version

### 1. File Format
- **Node.js**: TOML format (`fsc-assistant.env.toml`)
- **Python**: JSON/YAML format (`.fsc-assistant.json` or `.fsc-assistant.yaml`)

### 2. Environment Variable Naming
- **Node.js**: Uses `FSC_` prefix for environment variables
  - `FSC_LLM_PROVIDER`
  - `FSC_JIRA_TOKEN`
  - `FSC_GITHUB_TOKEN`

### 3. Configuration Structure
The Node.js version has a more structured approach with nested sections:
```toml
[llm]
provider = "openai"
model = "gpt-4"

[jira]  
base_url = "https://your-domain.atlassian.net"
token = "your-token"
```

### 4. Default Values
The Node.js version provides more explicit default values for better out-of-the-box experience.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FSC_LLM_PROVIDER` | LLM provider (openai, anthropic) | "openai" |
| `FSC_LLM_MODEL` | Model to use | "gpt-4" |
| `FSC_LLM_API_KEY` | API key for the LLM service | "" |
| `FSC_JIRA_BASE_URL` | JIRA instance URL | "" |
| `FSC_JIRA_TOKEN` | JIRA personal access token | "" |
| `FSC_GITHUB_TOKEN` | GitHub personal access token | "" |

## Command Line Options

The CLI supports various options:
```bash
fsc --help                    # Show help
fsc --config path/to/config   # Specify config file
fsc --verbose                 # Enable verbose logging
fsc --version                 # Show version
```

## Configuration Validation

The assistant validates configuration at startup and will report any issues with:
- Missing required API keys
- Invalid provider names  
- Malformed configuration files
- Incompatible settings

## Migration from Python Version

If you have an existing Python configuration:

1. **Convert JSON/YAML to TOML**:
   ```bash
   # Python config (JSON)
   {
     "llm": {
       "provider": "openai",
       "model": "gpt-4"
     }
   }

   # Node.js equivalent (TOML)  
   [llm]
   provider = "openai"
   model = "gpt-4"
   ```

2. **Update environment variable names**:
   - `FSC_LLM_API_KEY` instead of `LLM_API_KEY`
   - `FSC_JIRA_TOKEN` instead of `JIRA_TOKEN`

3. **Adjust file paths**:
   - Configuration files should be placed in `~/.fsc-assistant.env.toml`