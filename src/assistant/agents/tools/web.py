"""
Web page reading tools using Playwright for headless browser automation.

This module provides tools for fetching and extracting content from web pages,
including support for JavaScript-rendered content and web search functionality.
"""

import logging
import time
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Check if playwright is available
try:
    from markdownify import markdownify as md
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning(
        "Playwright not available. Install with: pip install 'fsc-assistant[web]' && "
        "playwright install chromium"
    )


def read_web_page(
    url: str,
    format: Literal["markdown", "text", "html"] = "markdown",
    wait_time: int = 2,
    timeout: int = 30000,
) -> str:
    """
    Fetch and extract content from a web page using headless Chrome.

    This function uses Playwright to render web pages, including JavaScript-heavy
    single-page applications (SPAs), and extracts the content in the specified format.

    Args:
        url: The URL to fetch (must include protocol, e.g., https://)
        format: Output format - "markdown" (default), "text", or "html"
        wait_time: Seconds to wait for JavaScript rendering (default: 2)
        timeout: Maximum time in milliseconds to wait for page load (default: 30000)

    Returns:
        str: Extracted content in the specified format, or error message if failed

    Examples:
        Read a documentation page as markdown:
        >>> content = read_web_page("https://docs.python.org/3/")
        >>> print(content[:100])

        Read an article as plain text:
        >>> content = read_web_page("https://example.com/article", format="text")

        Read with longer wait for heavy JavaScript:
        >>> content = read_web_page("https://spa-app.com", wait_time=5)

    Notes:
        - Requires Playwright and Chromium browser to be installed
        - Install with: pip install 'fsc-assistant[web]' && playwright install chromium
        - JavaScript is executed, so dynamic content is captured
        - Some websites may block headless browsers
        - Respects page load timeouts to prevent hanging
    """
    if not PLAYWRIGHT_AVAILABLE:
        return (
            "Error: Playwright is not installed. "
            "Install with: pip install 'fsc-assistant[web]' && playwright install chromium"
        )

    # Validate URL
    if not url.startswith(("http://", "https://")):
        return f"Error: Invalid URL '{url}'. URL must start with http:// or https://"

    # Validate format
    if format not in ("markdown", "text", "html"):
        return (
            f"Error: Invalid format '{format}'. Must be 'markdown', 'text', or 'html'"
        )

    try:
        logger.debug(
            f"Fetching web page: {url} (format={format}, wait_time={wait_time}s)"
        )

        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )

            try:
                # Create a new page
                page = browser.new_page()

                # Set a reasonable viewport size
                page.set_viewport_size({"width": 1280, "height": 720})

                # Navigate to the URL with timeout
                logger.debug(f"Navigating to {url}...")
                page.goto(url, timeout=timeout, wait_until="domcontentloaded")

                # Wait for JavaScript rendering
                if wait_time > 0:
                    logger.debug(f"Waiting {wait_time}s for JavaScript rendering...")
                    page.wait_for_timeout(wait_time * 1000)

                # Extract content based on format
                if format == "html":
                    content = page.content()
                elif format == "text":
                    # Get text content from body
                    content = page.evaluate("() => document.body.innerText")
                else:  # markdown
                    # Get HTML and convert to markdown
                    html_content = page.content()
                    content = md(html_content, heading_style="ATX", bullets="-")

                logger.debug(
                    f"Successfully extracted {len(content)} characters from {url}"
                )

                return content

            finally:
                # Always close the browser
                browser.close()

    except PlaywrightTimeoutError:
        error_msg = f"Error: Page load timed out after {timeout/1000}s for URL: {url}"
        logger.error(error_msg)
        return error_msg

    except Exception as e:
        error_msg = f"Error: Failed to fetch web page - {type(e).__name__}: {str(e)}"
        logger.exception(f"Unexpected error fetching {url}")
        return error_msg


def capture_web_page_screenshot(
    url: str,
    output_path: str,
    viewport_width: int = 1280,
    viewport_height: int = 720,
    full_page: bool = False,
    timeout: int = 30000,
) -> str:
    """
    Capture a screenshot of a web page.

    This function uses Playwright to render a web page and capture a screenshot,
    which can be useful for visual reference or debugging.

    Args:
        url: The URL to capture (must include protocol, e.g., https://)
        output_path: Path where the screenshot will be saved (PNG format)
        viewport_width: Browser viewport width in pixels (default: 1280)
        viewport_height: Browser viewport height in pixels (default: 720)
        full_page: If True, captures the entire scrollable page (default: False)
        timeout: Maximum time in milliseconds to wait for page load (default: 30000)

    Returns:
        str: Success message with path to saved screenshot, or error message if failed

    Examples:
        Capture a viewport screenshot:
        >>> result = capture_web_page_screenshot(
        ...     "https://example.com",
        ...     "screenshot.png"
        ... )

        Capture full page screenshot:
        >>> result = capture_web_page_screenshot(
        ...     "https://example.com/article",
        ...     "full_article.png",
        ...     full_page=True
        ... )

        Capture with custom viewport:
        >>> result = capture_web_page_screenshot(
        ...     "https://example.com",
        ...     "mobile.png",
        ...     viewport_width=375,
        ...     viewport_height=667
        ... )

    Notes:
        - Requires Playwright and Chromium browser to be installed
        - Screenshot is saved as PNG format
        - Full page screenshots can be very large for long pages
        - Creates parent directories if they don't exist
    """
    if not PLAYWRIGHT_AVAILABLE:
        return (
            "Error: Playwright is not installed. "
            "Install with: pip install 'fsc-assistant[web]' && playwright install chromium"
        )

    # Validate URL
    if not url.startswith(("http://", "https://")):
        return f"Error: Invalid URL '{url}'. URL must start with http:// or https://"

    try:
        logger.debug(f"Capturing screenshot of: {url}")

        # Ensure output directory exists
        output_file = Path(output_path).expanduser().resolve()
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )

            try:
                # Create a new page with specified viewport
                page = browser.new_page()
                page.set_viewport_size(
                    {"width": viewport_width, "height": viewport_height}
                )

                # Navigate to the URL
                logger.debug(f"Navigating to {url}...")
                page.goto(url, timeout=timeout, wait_until="domcontentloaded")

                # Wait a bit for rendering
                page.wait_for_timeout(2000)

                # Capture screenshot
                logger.debug(f"Capturing screenshot to {output_file}...")
                page.screenshot(path=str(output_file), full_page=full_page)

                logger.debug(f"Screenshot saved to {output_file}")

                return f"Screenshot saved to: {output_file}"

            finally:
                # Always close the browser
                browser.close()

    except PlaywrightTimeoutError:
        error_msg = f"Error: Page load timed out after {timeout/1000}s for URL: {url}"
        logger.error(error_msg)
        return error_msg

    except Exception as e:
        error_msg = (
            f"Error: Failed to capture screenshot - {type(e).__name__}: {str(e)}"
        )
        logger.exception(f"Unexpected error capturing screenshot of {url}")
        return error_msg


def search_google(query: str) -> str:
    """
    Perform a web search and aggregate content from the top 5 results.

    This function attempts to search using Google first, then falls back to DuckDuckGo
    if Google is unavailable (e.g., CAPTCHA). It extracts the top 5 organic search
    result URLs, fetches content from each result page, and combines all content into
    a single markdown document with source attribution.

    Args:
        query: The search query string

    Returns:
        str: Combined markdown document with content from top 5 search results,
             or error message if search fails

    Examples:
        Search for Python documentation:
        >>> results = search_google("Python asyncio tutorial")
        >>> print(results[:200])

        Search for recent news:
        >>> results = search_google("latest AI developments 2024")

        Search for technical solutions:
        >>> results = search_google("how to fix playwright timeout error")

    Notes:
        - Requires Playwright and Chromium browser to be installed
        - Tries Google first, falls back to DuckDuckGo if Google blocks the request
        - Fetches and combines content from top 5 organic search results
        - Total operation time: typically 15-35 seconds
        - Continues fetching even if some individual pages fail
        - Respects rate limits with delays between requests
        - Does not store search history or results

    Performance:
        - Search execution: ~2-3 seconds
        - Fetching 5 pages: ~10-30 seconds (2-6 seconds per page)
        - Memory usage: ~200-400MB during operation

    Output Format:
        The returned markdown document has the following structure:

        # Search Results for: [query]
        Search engine: [Google/DuckDuckGo]

        ## Result 1: [Page Title]
        Source: [URL]

        [Content in markdown format]

        ---

        ## Result 2: [Page Title]
        ...
    """
    if not PLAYWRIGHT_AVAILABLE:
        return (
            "Error: Playwright is not installed. "
            "Install with: pip install 'fsc-assistant[web]' && playwright install chromium"
        )

    # Validate and sanitize query
    if not query or not query.strip():
        return "Error: Search query cannot be empty"

    query = query.strip()

    try:
        logger.info(f"Performing web search for: {query}")

        # Step 1: Try Google first, fall back to DuckDuckGo
        result_urls = None
        search_engine = None

        try:
            logger.info("Attempting Google search...")
            result_urls = _extract_google_search_results(query)
            search_engine = "Google"
            logger.info(f"Google search successful, found {len(result_urls)} results")
        except Exception as google_error:
            logger.warning(f"Google search failed: {google_error}")
            logger.info("Falling back to DuckDuckGo...")
            try:
                result_urls = _extract_duckduckgo_search_results(query)
                search_engine = "DuckDuckGo"
                logger.info(
                    f"DuckDuckGo search successful, found {len(result_urls)} results"
                )
            except Exception as ddg_error:
                logger.error(f"DuckDuckGo search also failed: {ddg_error}")
                return (
                    f"Error: Both search engines failed.\n"
                    f"Google: {str(google_error)}\n"
                    f"DuckDuckGo: {str(ddg_error)}"
                )

        if not result_urls:
            return f"No search results found for query: {query}"

        # Step 2: Fetch and combine content from each result
        combined_content = (
            f"# Search Results for: {query}\nSearch engine: {search_engine}\n\n"
        )

        for i, url in enumerate(result_urls[:5], 1):
            logger.info(f"Fetching result {i}/5: {url}")

            try:
                # Add delay between requests to avoid rate limiting
                if i > 1:
                    time.sleep(1.5)  # 1.5 second delay between requests

                # Fetch content using existing read_web_page function
                content = read_web_page(
                    url, format="markdown", wait_time=2, timeout=15000
                )

                # Check if content fetch was successful
                if content.startswith("Error:"):
                    logger.warning(f"Failed to fetch result {i}: {content}")
                    combined_content += (
                        f"## Result {i}\nSource: {url}\n\n*{content}*\n\n---\n\n"
                    )
                else:
                    # Extract title from content (first heading) or use URL
                    title = _extract_title_from_content(content) or url
                    combined_content += (
                        f"## Result {i}: {title}\nSource: {url}\n\n{content}\n\n---\n\n"
                    )
                    logger.info(f"Successfully fetched result {i}")

            except Exception as e:
                error_msg = f"Failed to fetch: {type(e).__name__}: {str(e)}"
                logger.error(f"Error fetching result {i} ({url}): {error_msg}")
                combined_content += (
                    f"## Result {i}\nSource: {url}\n\n*{error_msg}*\n\n---\n\n"
                )

        logger.info(
            f"Search completed. Combined content length: {len(combined_content)} characters"
        )
        return combined_content

    except Exception as e:
        error_msg = f"Error: Search failed - {type(e).__name__}: {str(e)}"
        logger.exception(f"Unexpected error during web search for '{query}'")
        return error_msg


def _extract_google_search_results(query: str) -> list[str]:
    """
    Extract organic search result URLs from Google search page.

    Args:
        query: The search query string

    Returns:
        list[str]: List of URLs from organic search results (up to 10)

    Raises:
        Exception: If search fails or results cannot be extracted
    """
    # URL encode the query
    encoded_query = quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"

    logger.debug(f"Navigating to Google search: {search_url}")

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        try:
            # Create context with realistic settings
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                locale="en-US",
                timezone_id="America/New_York",
            )

            # Add extra properties to make browser look more real
            page = context.new_page()

            # Override navigator.webdriver property
            page.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
            )

            # Navigate to Google search
            logger.debug("Navigating to Google...")
            page.goto(search_url, timeout=20000, wait_until="domcontentloaded")

            # Wait for search results to load
            logger.debug("Waiting for search results...")
            page.wait_for_timeout(3000)

            # Check for CAPTCHA
            if (
                "sorry/index" in page.url
                or page.locator("text=unusual traffic").count() > 0
            ):
                raise Exception("Google CAPTCHA detected")

            # Extract organic search result URLs
            result_urls = []

            # Try standard search result selectors
            try:
                search_results = page.locator("div.g").all()
                logger.debug(f"Found {len(search_results)} div.g elements")

                for result in search_results[:10]:
                    try:
                        link = result.locator("a").first
                        href = link.get_attribute("href")

                        if (
                            href
                            and href.startswith("http")
                            and "google.com" not in href
                        ):
                            result_urls.append(href)
                            logger.debug(f"Extracted URL: {href}")

                    except Exception as e:
                        logger.debug(f"Failed to extract URL from result: {e}")
                        continue

            except Exception as e:
                logger.warning(f"Google extraction failed: {e}")

            # Remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in result_urls:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)

            logger.debug(f"Extracted {len(unique_urls)} unique URLs from Google")

            if not unique_urls:
                raise Exception("No search results could be extracted from Google")

            return unique_urls

        finally:
            context.close()
            browser.close()


def _extract_duckduckgo_search_results(query: str) -> list[str]:
    """
    Extract organic search result URLs from DuckDuckGo search page.

    Args:
        query: The search query string

    Returns:
        list[str]: List of URLs from organic search results (up to 10)

    Raises:
        Exception: If search fails or results cannot be extracted
    """
    # URL encode the query
    encoded_query = quote_plus(query)
    search_url = f"https://duckduckgo.com/?q={encoded_query}"

    logger.debug(f"Navigating to DuckDuckGo search: {search_url}")

    with sync_playwright() as p:
        # Launch browser in headless mode (DuckDuckGo is less strict)
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        try:
            # Create page with realistic user agent
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page.set_viewport_size({"width": 1280, "height": 720})

            # Navigate to DuckDuckGo search
            logger.debug("Navigating to DuckDuckGo...")
            page.goto(search_url, timeout=20000, wait_until="domcontentloaded")

            # Wait for search results to load
            logger.debug("Waiting for search results...")
            page.wait_for_timeout(4000)

            # Extract organic search result URLs
            result_urls = []

            # DuckDuckGo uses different selectors
            try:
                # Try multiple selector strategies for DuckDuckGo

                # Strategy 1: article elements with data-testid
                search_results = page.locator("article[data-testid='result']").all()
                logger.debug(f"Found {len(search_results)} article elements")

                for result in search_results[:10]:
                    try:
                        # Find the main link
                        link = result.locator("a[data-testid='result-title-a']").first
                        href = link.get_attribute("href")

                        if href and href.startswith("http"):
                            result_urls.append(href)
                            logger.debug(f"Extracted URL: {href}")

                    except Exception as e:
                        logger.debug(f"Failed to extract URL from result: {e}")
                        continue

            except Exception as e:
                logger.warning(f"DuckDuckGo Strategy 1 failed: {e}")

            # Strategy 2: Fallback to finding links in results
            if not result_urls:
                try:
                    logger.debug("Trying DuckDuckGo Strategy 2: all result links")
                    # Look for links in the results area
                    all_links = page.locator("#links a[href^='http']").all()
                    logger.debug(f"Found {len(all_links)} links in results area")

                    for link in all_links[:15]:
                        href = link.get_attribute("href")

                        # Filter for organic results
                        if (
                            href
                            and href.startswith("http")
                            and "duckduckgo.com" not in href
                            and len(result_urls) < 10
                        ):
                            result_urls.append(href)
                            logger.debug(f"Extracted URL: {href}")

                except Exception as e:
                    logger.warning(f"DuckDuckGo Strategy 2 failed: {e}")

            # Remove duplicates while preserving order
            seen = set()
            unique_urls = []
            for url in result_urls:
                if url not in seen:
                    seen.add(url)
                    unique_urls.append(url)

            logger.debug(f"Extracted {len(unique_urls)} unique URLs from DuckDuckGo")

            if not unique_urls:
                raise Exception("No search results could be extracted from DuckDuckGo")

            return unique_urls

        finally:
            browser.close()


def _extract_title_from_content(content: str) -> str | None:
    """
    Extract the first heading from markdown content to use as title.

    Args:
        content: Markdown content string

    Returns:
        str | None: The first heading text, or None if no heading found
    """
    lines = content.split("\n")
    for line in lines[:20]:  # Check first 20 lines
        line = line.strip()
        if line.startswith("#"):
            # Remove markdown heading markers and return text
            title = line.lstrip("#").strip()
            if title:
                return title
    return None
