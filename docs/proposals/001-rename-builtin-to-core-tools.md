# Rename `builtin` to `core_tools`

## Summary

This document proposes renaming the `builtin` module to `core_tools` and adding a new `download_web_file` tool to improve code organization, clarity, and functionality.

## Problem Statement

The current project structure uses a `builtin` module which is misleading since it's not actually Python builtin functions. Additionally, there's no standard way to download files from web URLs in the existing tools set.

## Changes Proposed

1. **Rename Module**: Rename `src/assistant/tools/builtin.py` to `src/assistant/tools/core_tools.py`
2. **Add New Tool**: Add a `download_web_file` function that allows downloading files from web URLs
3. **Update Imports**: Update all import statements throughout the codebase to reference the new module name
4. **Tool Registration**: Register the new tool in the automatic discovery system

## Implementation Details

### 1. Module Renaming

The file `src/assistant/tools/builtin.py` will be renamed to `src/assistant/tools/core_tools.py`.

### 2. New Tool: download_web_file

A new function `download_web_file(url: str, destination_path: str)` will be added that:
- Downloads files from web URLs using curl with progress bar
- Creates directories as needed for the destination path
- Returns success or error messages
- Integrates with existing command execution utilities

### 3. Tool Classes

The new tool will include proper BaseTool subclasses:
- `DownloadWebFileTool` - The actual tool class that extends BaseTool
- Integration into automatic discovery system via TOOL_REGISTRY

## Migration Steps

1. Update all import statements from `.builtin` to `.core_tools`
2. Update any references in documentation or comments
3. Ensure the new tool is properly registered and discoverable
4. Test that existing functionality remains intact

## Backward Compatibility

This change maintains full backward compatibility for existing tools while adding new functionality.

## Testing Plan

1. Verify all existing tools still work correctly
2. Test the new `download_web_file` function with various URLs
3. Ensure automatic tool discovery works properly
4. Run integration tests to confirm no regressions

## Acceptance Criteria

- [ ] Module renamed from `builtin.py` to `core_tools.py`
- [ ] New `download_web_file` function implemented and working
- [ ] All imports updated correctly throughout the codebase
- [ ] Tool discovery system properly registers new tool
- [ ] No existing functionality broken