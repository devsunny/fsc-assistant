## Context

The current web search implementation in `src/assistant/agents/tools/web.py` uses Playwright to scrape Google search results, which is brittle and prone to failure due to:
- CAPTCHA challenges blocking automated access
- HTML structure changes breaking selectors
- Anti-bot detection mechanisms
- Rate limiting without clear quotas
- Legal and terms-of-service concerns with scraping

Google provides an official Custom Search JSON API that offers:
- Reliable, structured search results
- Clear rate limits and quota management
- Official support and documentation
- No CAPTCHA or anti-bot issues
- Consistent API format

## Goals / Non-Goals

**Goals:**
- Provide a reliable, production-ready web search capability using Google's official API
- Maintain backward compatibility with existing Playwright-based search
- Offer clear configuration management for API credentials
- Implement proper error handling and user-friendly error messages
- Support key search features: result count, safe search, site restriction

**Non-Goals:**
- Replace the existing `search_google()` function entirely (it remains as fallback)
- Implement complex search features not supported by the Custom Search API
- Create a separate search UI or interface beyond the function API
- Handle billing or quota management beyond error messaging

## Decisions

### 1. API Selection
**Decision:** Use Google Custom Search JSON API instead of continuing with web scraping

**Rationale:**
- Official API provides stability and reliability
- Clear documentation and support from Google
- Structured JSON responses vs. HTML parsing
- No CAPTCHA or anti-bot issues
- Better error handling and status codes

**Alternatives Considered:**
- Continue with Playwright scraping: Too brittle, frequent breakages
- Use SerpAPI or similar third-party service: Additional cost and dependency
- Use Bing Search API: Less familiar to users, different result quality

### 2. Configuration Structure
**Decision:** Add `google` section to existing AssistantConfig with `api_key` and `search_engine_id`

**Rationale:**
- Consistent with existing configuration patterns (jira, github, llm sections)
- Easy to manage via existing config CLI commands
- Clear separation of concerns
- Supports both project-level and global configuration

**Implementation:**
```toml
[google]
api_key = "your-api-key"
search_engine_id = "your-search-engine-id"
```

### 3. Module Organization
**Decision:** Create new module `src/assistant/agents/web/google_search.py` separate from existing `web.py`

**Rationale:**
- Separation of concerns: API-based vs. scraping-based search
- Easier maintenance and testing
- Clear dependency management (google-api-python-client only needed for new module)
- Follows existing pattern (web/ directory has separate modules for different tools)

### 4. Dependency Management
**Decision:** Make google-api-python-client optional with graceful degradation

**Rationale:**
- Don't force all users to install Google API client if they don't need search
- Maintain backward compatibility
- Provide clear error messages guiding users to install when needed
- Aligns with existing pattern (Playwright is also optional)

**Implementation:**
```python
try:
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
```

### 5. Error Handling Strategy
**Decision:** Implement specific error handling for different failure modes

**Rationale:**
- Different errors require different user actions
- Clear error messages improve user experience
- Helps users understand if they need to: configure credentials, fix credentials, wait for quota reset, or check network

**Error Types:**
- Missing configuration → Instructions on obtaining and setting credentials
- Invalid credentials → Suggest verifying API key and search engine ID
- Quota exceeded → Explain limits and point to upgrade options
- Network errors → Generic connection error message
- Missing dependency → Installation instructions

### 6. Result Formatting
**Decision:** Format results as markdown with consistent structure

**Rationale:**
- Consistent with existing `search_google()` output format
- Easy to read and process by LLMs
- Clear attribution of sources
- Supports the same use cases as current implementation

**Format:**
```markdown
# Search Results for: [query]
Search engine: Google Custom Search API

## Result 1: [Title]
Source: [URL]

[Snippet/content]

---

## Result 2: [Title]
...
```

## Risks / Trade-offs

**Risk:** API credentials require setup and may involve costs
- **Mitigation:** Provide clear setup documentation; free tier includes 100 queries/day; maintain fallback to existing search

**Risk:** Different search results quality compared to regular Google search
- **Mitigation:** Custom Search API can be configured to search entire web; results may differ but should be comparable

**Risk:** Additional external API dependency
- **Mitigation:** Graceful fallback when API unavailable; optional dependency installation

**Risk:** Rate limiting and quota management complexity
- **Mitigation:** Clear error messages; document quota limits; suggest monitoring usage

## Migration Plan

No migration needed - this is an additive change:
1. New function `search_google_custom_api()` is added alongside existing `search_google()`
2. Existing functionality remains unchanged
3. Users can gradually adopt the new API-based search
4. No breaking changes to configuration or APIs

## Open Questions

1. Should we eventually deprecate the Playwright-based search? 
   - **Current decision:** No, keep as fallback for users without API access

2. How should we handle the 100 queries/day free tier limit in documentation?
   - **Approach:** Clearly document in setup instructions and error messages

3. Should we provide a way to programmatically switch between search implementations?
   - **Current decision:** Let users/tools choose which function to call; no automatic switching

4. Do we need to handle pagination for more than 10 results?
   - **Current decision:** No, limit to 10 results max to match current behavior
