# Change Working Directory Tool Function

## Summary

This change adds a new tool function to allow agents to change the working directory of the system shell. This capability will enable agents to execute commands in specific project directories, improving context awareness and command execution accuracy.

## Problem Statement

Currently, the assistant's agent tools operate with a fixed working directory context. When executing shell commands that require specific project contexts or when navigating between different projects, there is no way for agents to change their current working directory. This limitation reduces the effectiveness of shell-based tool usage in multi-project environments.

## Solution Overview

Add a new `change_working_directory` function that:
- Allows changing the current working directory to any valid path
- Validates that the target directory exists and is accessible  
- Returns appropriate success/failure messages with context information
- Maintains proper error handling for invalid paths or permission issues
- Integrates seamlessly with existing shell command execution tools

## Change ID

change-working-directory

## Related Changes

- Existing: `add-system-shell-tool-function` - Enhances system shell capabilities