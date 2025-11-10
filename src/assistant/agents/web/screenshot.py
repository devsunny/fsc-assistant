import logging
from pathlib import Path

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
