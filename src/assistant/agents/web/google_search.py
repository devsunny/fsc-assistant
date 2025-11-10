"""
Google Custom Search API integration for reliable web search.

This module provides a tool function to search using Google's official Custom Search JSON API
as an alternative to web scraping. It requires API credentials and handles various error
conditions gracefully.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Check if google-api-python-client is available
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logger.warning(
        "google-api-python-client not available. "
        "Install with: pip install google-api-python-client"
    )

# Import configuration manager
from assistant.config.manager import AssistantConfig


def search_google_custom_api(
    query: str,
    num_results: int = 5,
    safe_search: Optional[str] = "moderate",
    site_restrict: Optional[str] = None,
) -> str:
    """
    Search using Google Custom Search JSON API.

    This function uses Google's official Custom Search API to perform web searches,
    providing reliable results without the brittleness of web scraping. It requires
    valid API credentials to be configured.

    Args:
        query: The search query string
        num_results: Number of results to return (1-10, default: 5)
        safe_search: Safe search level - "off", "moderate", or "strict" (default: "moderate")
        site_restrict: Optional site restriction (e.g., "example.com" or "site1.com,site2.com")

    Returns:
        str: Formatted markdown document with search results, or error message

    Examples:
        Basic search:
        >>> results = search_google_custom_api("Python asyncio tutorial")
        >>> print(results[:200])

        Search with custom result count:
        >>> results = search_google_custom_api("machine learning", num_results=10)

        Search with site restriction:
        >>> results = search_google_custom_api("python docs", site_restrict="python.org")

        Search with strict safe search:
        >>> results = search_google_custom_api("programming tutorials", safe_search="strict")

    Notes:
        - Requires google-api-python-client to be installed
        - Requires valid Google Custom Search API credentials (api_key and search_engine_id)
        - Free tier includes 100 queries per day
        - Returns error messages for missing/invalid credentials or exceeded quota
    """
    # Check if dependency is available
    if not GOOGLE_API_AVAILABLE:
        return (
            "Error: google-api-python-client is not installed. "
            "Install with: pip install google-api-python-client"
        )

    # Validate query
    if not query or not query.strip():
        return "Error: Search query cannot be empty"

    # Validate num_results
    if not 1 <= num_results <= 10:
        return "Error: num_results must be between 1 and 10"

    # Validate safe_search
    valid_safe_levels = ["off", "moderate", "strict"]
    if safe_search not in valid_safe_levels:
        return f"Error: safe_search must be one of {valid_safe_levels}"

    query = query.strip()
    logger.info(f"Performing Google Custom Search for: {query}")

    try:
        # Load configuration
        config = AssistantConfig()
        api_key = config.get_option("google", "api_key", "")
        search_engine_id = config.get_option("google", "search_engine_id", "")

        # Check if credentials are configured
        if not api_key or not search_engine_id:
            return (
                "Error: Google Custom Search API credentials are not configured.\n\n"
                "To use this feature, you need to:\n"
                "1. Get a Google Custom Search API key from:\n"
                "   https://developers.google.com/custom-search/v1/overview\n"
                "2. Create a Custom Search Engine at:\n"
                "   https://programmablesearchengine.google.com/\n"
                "3. Configure the credentials using:\n"
                "   fsc-assistant config set google.api_key YOUR_API_KEY\n"
                "   fsc-assistant config set google.search_engine_id YOUR_ENGINE_ID\n\n"
                "Note: The free tier includes 100 queries per day."
            )

        # Build the service
        service = build("customsearch", "v1", developerKey=api_key)

        # Prepare search parameters
        search_params = {
            "q": query,
            "cx": search_engine_id,
            "num": min(num_results, 10),  # API max is 10
        }

        # Add safe search parameter
        safe_search_map = {
            "off": "off",
            "moderate": "moderate",
            "strict": "high",
        }
        search_params["safe"] = safe_search_map.get(safe_search, "moderate")

        # Add site restriction if provided
        if site_restrict:
            search_params["siteSearch"] = site_restrict
            search_params["siteSearchFilter"] = "i"  # include only

        # Execute search
        logger.debug(f"Executing search with params: {search_params}")
        result = service.cse().list(**search_params).execute()

        # Check if results were found
        if "items" not in result or not result["items"]:
            return f"No search results found for query: {query}"

        # Format results as markdown
        items = result["items"][:num_results]
        markdown_output = f"# Search Results for: {query}\n"
        markdown_output += "Search engine: Google Custom Search API\n\n"

        for i, item in enumerate(items, 1):
            title = item.get("title", "No title")
            link = item.get("link", "")
            snippet = item.get("snippet", "No snippet available")

            markdown_output += f"## Result {i}: {title}\n"
            markdown_output += f"Source: {link}\n\n"
            markdown_output += f"{snippet}\n\n"
            markdown_output += "---\n\n"

        logger.info(f"Search completed successfully. Found {len(items)} results.")
        return markdown_output

    except HttpError as e:
        error_reason = e.reason
        error_code = e.resp.status if e.resp else "unknown"

        if error_code == 403:
            if "quota" in error_reason.lower():
                return (
                    "Error: Google Custom Search API quota exceeded.\n\n"
                    "The free tier includes 100 queries per day.\n"
                    "To continue using the API:\n"
                    "1. Wait for the daily quota to reset (24 hours)\n"
                    "2. Upgrade to a paid tier for higher limits:\n"
                    "   https://developers.google.com/custom-search/v1/overview#pricing\n\n"
                    "Consider using the fallback search_google() function "
                    "if you need to perform searches now."
                )
            else:
                return (
                    "Error: Authentication failed with Google Custom Search API.\n\n"
                    "Please verify your credentials:\n"
                    "1. Check that your API key is correct\n"
                    "2. Verify your Search Engine ID is valid\n"
                    "3. Ensure the Custom Search API is enabled in your Google Cloud project\n\n"
                    "You can check and update your credentials using:\n"
                    "fsc-assistant config get google.api_key\n"
                    "fsc-assistant config get google.search_engine_id"
                )
        elif error_code == 400:
            return (
                f"Error: Invalid request to Google Custom Search API.\n\n"
                f"Details: {error_reason}\n\n"
                f"Please check your search parameters."
            )
        else:
            return (
                f"Error: Google Custom Search API request failed.\n\n"
                f"Status code: {error_code}\n"
                f"Reason: {error_reason}\n\n"
                f"Please check your network connection and API credentials."
            )

    except Exception as e:
        logger.exception(f"Unexpected error during Google Custom Search: {e}")
        return (
            f"Error: An unexpected error occurred during search.\n\n"
            f"Details: {type(e).__name__}: {str(e)}\n\n"
            f"Please check your configuration and try again."
        )
