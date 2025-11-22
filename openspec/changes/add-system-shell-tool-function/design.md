# Design: Add System Shell Tool Function

## Overview

This design document outlines the enhancement of the existing `run_shell_command` function in `src/assistant/agents/tools/system_shell.py`. The goal is to improve robustness, add timeout support, and enhance error handling while maintaining full backward compatibility.

## Current Implementation Analysis

The current implementation:
- Supports both interactive and non-interactive modes
- Uses existing utility functions from `assistant.utils.cli.executor`
- Has basic logging capabilities
- Provides good documentation but lacks advanced features

## Enhanced Functionality Requirements

### ADDED Requirements

#### 1. Timeout Support
**Scenario:** Commands that hang or take too long to execute should not block the agent indefinitely.
- Add optional timeout parameter (default: None for no timeout)
- Implement proper timeout handling with `subprocess` timeouts
- Return meaningful error messages when commands exceed timeout limits

#### 2. Enhanced Error Handling  
**Scenario:** Various failure modes need better reporting and categorization.
- Catch specific exceptions (e.g., FileNotFoundError, PermissionError)
- Provide more detailed error context in return values
- Distinguish between execution errors vs configuration errors

#### 3. Improved Logging
**Scenario:** Better monitoring of command executions for debugging and auditing.
- Add more granular logging levels (DEBUG, INFO, WARNING, ERROR)
- Log execution start/end times
- Include process ID and resource usage information when available

#### 4. Parameter Validation
**Scenario:** Prevent invalid or malicious inputs from causing issues.
- Validate command string input to prevent injection attacks
- Sanitize command parameters where appropriate
- Add bounds checking for timeout values

### MODIFIED Requirements

#### 1. Function Signature Enhancement
**Scenario:** The function signature needs to be enhanced to support new features while maintaining backward compatibility.
- Add optional `timeout` parameter with default None
- Maintain existing behavior when no timeout is specified
- Ensure all existing calling code continues to work unchanged

#### 2. Return Value Enhancement  
**Scenario:** Return values should provide more context about execution success/failure.
- Include exit codes in return values for non-interactive mode
- Provide better error messages with actionable information
- Maintain backward compatibility of return value format

## Implementation Approach

### Architecture Considerations

1. **Backward Compatibility**: All changes must maintain existing API contracts
2. **Performance Impact**: Minimal overhead from new features  
3. **Security**: Input validation to prevent command injection
4. **Error Resilience**: Graceful degradation when timeouts occur

### Technical Details

#### Timeout Implementation
- Use `subprocess.run()` with timeout parameter for non-interactive mode
- For interactive mode, implement a different approach since it doesn't support timeout directly
- Return clear error messages when timeouts occur

#### Error Handling Strategy  
- Catch specific exceptions and provide meaningful context
- Log errors at appropriate levels (DEBUG/ERROR)
- Preserve original exception information where useful

#### Logging Implementation
- Add DEBUG level logging for command execution details
- Include timestamps, process IDs, and execution duration
- Use structured logging format when possible

## Trade-offs Considered

1. **Security vs Usability**: 
   - Input validation adds security but may reject valid commands
   - Need to balance thoroughness with usability

2. **Performance vs Features**:
   - Additional logging has minimal performance impact
   - Timeout handling requires careful implementation to avoid resource leaks

3. **Complexity vs Robustness**:
   - Enhanced error handling increases code complexity 
   - But improves overall system robustness and debuggability

## Dependencies

1. `subprocess` module (already imported)
2. Existing CLI executor utilities in `assistant.utils.cli.executor`
3. Logging infrastructure already configured
4. No new external dependencies required

## Testing Strategy

### Unit Tests Required
- Basic command execution without timeout
- Timeout scenarios with different timeout values  
- Error handling for invalid commands
- Interactive mode behavior unchanged
- Parameter validation tests