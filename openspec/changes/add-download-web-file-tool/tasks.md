## 1. Implementation
- [x] 1.1 Add `httpx` dependency to `pyproject.toml`
- [x] 1.2 Implement `download_web_file` function in `src/assistant/agents/tools/web.py`
- [x] 1.3 Add protocol validation for http, https, ftp, and data: schemes
- [x] 1.4 Implement binary file download with proper content-type handling
- [x] 1.5 Implement text file download with encoding detection
- [x] 1.6 Add data URI parsing and decoding support
- [x] 1.7 Implement FTP download functionality
- [x] 1.8 Add comprehensive error handling with stack trace reporting
- [x] 1.9 Add detailed docstring with examples
- [x] 1.10 Test function with various file types and protocols

## 2. Validation
- [x] 2.1 Run `openspec validate add-download-web-file-tool --strict`
- [x] 2.2 Verify all requirements have at least one scenario
- [x] 2.3 Confirm spec format follows OpenSpec conventions
- [x] 2.4 Test download functionality with HTTP/HTTPS URLs
- [x] 2.5 Test download functionality with FTP URLs
- [x] 2.6 Test download functionality with data URIs
- [x] 2.7 Verify error messages include stack traces on failure
- [x] 2.8 Confirm destination path is returned correctly on success