"""Web tools module with lazy loading for performance."""

from typing import Any


# Lazy loading functions
def fetch_webpage_content(*args: Any, **kwargs: Any) -> Any:
    """Fetch and extract content from a web page using headless Chrome."""
    from .webpage import fetch_webpage_content as _fetch

    return _fetch(*args, **kwargs)


def capture_web_page_screenshot(*args: Any, **kwargs: Any) -> Any:
    """Capture a screenshot of a web page."""
    from .screenshot import capture_web_page_screenshot as _capture

    return _capture(*args, **kwargs)


def download_web_file_from_url(*args: Any, **kwargs: Any) -> Any:
    """Download a file from a web URL and save it to the specified destination."""
    from .download import download_web_file_from_url as _download

    return _download(*args, **kwargs)


def search_google_custom_api(*args: Any, **kwargs: Any) -> Any:
    """Web search with Google Custom Search API."""
    from .google_search import search_google_custom_api as _search

    return _search(*args, **kwargs)


__all__ = [
    "fetch_webpage_content",
    "capture_web_page_screenshot",
    "download_web_file_from_url",
    "search_google_custom_api",
]
