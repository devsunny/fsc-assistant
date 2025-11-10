import logging
from typing import Literal


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


def fetch_webpage_content(
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
