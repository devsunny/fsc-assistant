# Design: LLM Command Output Analysis

## Overview
This design implements the ability to analyze shell command outputs with AI by adding an `ask ai` command that leverages existing LLM infrastructure.

## Architecture
The solution extends the AgenticShell class with:
1. A `last_command_output` attribute to store captured output
2. Enhanced command processing logic for `ask ai`
3. Integration with existing LLM workflow components

## Implementation Details

### Shell State Management
- Add `self.last_command_output = None` in `__init__`
- Capture stdout/stderr from system commands when using `!command` syntax  
- Overwrite previous output with each new command execution to prevent memory issues

### Command Processing Extension
When `ask ai` is detected:
1. Check if `last_command_output` exists 
2. If not, display helpful message indicating no output available
3. If yes, prepare prompt with captured output and send to LLM via existing `run_workflow()` method
4. Display response using existing UI components (Panel + Markdown)

### Integration Points
- Uses existing `execute_command_interactive` for command execution 
- Leverages existing `run_workflow` method for LLM processing
- Utilizes existing `Panel` and `Markdown` components for display
- Reuses existing system prompts and tool configuration

## Data Flow
1. User types `!ls -la`
2. Shell executes command, captures output, stores in `last_command_output`
3. User types `ask ai` 
4. Shell checks `last_command_output`, prepares prompt with content
5. Shell calls `run_workflow()` with analysis prompt  
6. LLM processes and returns response
7. Shell displays response using Panel + Markdown

## Backward Compatibility
This change maintains full backward compatibility:
- All existing shell commands work exactly as before
- No changes to core LLM infrastructure or workflows
- No modifications to system prompts or tool configurations