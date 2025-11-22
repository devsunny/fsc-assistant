## Why
The current web tools module provides functionality for reading web pages and capturing screenshots, but lacks the ability to download files directly from web URLs. This capability would enable the assistant to retrieve binary files, documents, and other resources from HTTP/HTTPS URLs, as well as support FTP and data URI protocols for comprehensive file acquisition.

## What Changes
- Add a new `download_web_file` function to `assistant.agents.tools.web` module
- Support multiple protocols: HTTP, HTTPS, FTP, and data: URIs
- Handle both text and binary file types with automatic content type detection
- Return destination path on success, detailed error messages with stack traces on failure
- Integrate with existing web tools error handling and logging patterns

## Impact
- Affected specs: web-tools (new capability)
- Affected code: `src/assistant/agents/tools/web.py` (new function addition)
- New dependency: `httpx` library for HTTP/FTP downloads
- No breaking changes to existing functionality