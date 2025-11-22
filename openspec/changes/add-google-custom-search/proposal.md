## Why
The current web search functionality in `search_google()` uses Playwright to perform web scraping of Google search results, which is brittle and can be blocked by CAPTCHAs or anti-bot measures. This approach is unreliable for production use and requires maintaining complex scraping logic that breaks when Google changes their HTML structure.

## What Changes
- Add a new `google_search()` function that uses Google's official Custom Search JSON API
- Add Google API configuration section to AssistantConfig with `api_key` and `search_engine_id`
- Create new module `src/assistant/agents/web/google_search.py` for the implementation
- Add `google-api-python-client` dependency to pyproject.toml
- Provide fallback behavior to existing Playwright-based search if API credentials are not configured

## Impact
- Affected specs: web-search (new capability)
- Affected code: New file `src/assistant/agents/web/google_search.py`
- Configuration: Adds `google` section to `.fsc-assistant.env.toml` with `api_key` and `search_engine_id`
- New dependency: `google-api-python-client>=2.100.0`
- No breaking changes to existing functionality - provides enhanced alternative
- Existing `search_google()` function remains unchanged as fallback