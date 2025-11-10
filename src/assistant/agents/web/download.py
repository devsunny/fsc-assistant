import base64
import logging
import re
import time
import traceback
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus, urlparse

logger = logging.getLogger(__name__)
# Check if httpx is available
try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logger.warning(
        "httpx not available. Install with: pip install 'fsc-assistant[web]'"
    )

# Check if ftplib is available (usually built-in)
try:
    import ftplib

    FTPLIB_AVAILABLE = True
except ImportError:
    FTPLIB_AVAILABLE = False
    logger.warning("ftplib not available. FTP downloads will not be supported.")


def download_web_file_from_url(
    url: str,
    destination: str,
    timeout: int = 30000,
) -> str:
    """
    Download a file from a web URL and save it to the specified destination.

    This function supports multiple protocols including HTTP, HTTPS, FTP, and data URIs.
    It automatically detects content type and handles both binary and text files appropriately.
    The function creates parent directories if they don't exist and returns the absolute
    path to the saved file on success.

    Args:
        url: The URL to download from (supports http://, https://, ftp://, and data:)
        destination: Path where the file will be saved
        timeout: Maximum time in milliseconds to wait for download (default: 30000)

    Returns:
        str: Absolute path to the saved file on success, or detailed error message with stack trace on failure

    Examples:
        Download a PDF document:
        >>> result = download_web_file_from_url(
        ...     "https://example.com/document.pdf",
        ...     "downloads/document.pdf"
        ... )

        Download an image:
        >>> result = download_web_file_from_url(
        ...     "https://example.com/image.jpg",
        ...     "images/photo.jpg"
        ... )

        Download from FTP:
        >>> result = download_web_file_from_url(
        ...     "ftp://ftp.example.com/file.txt",
        ...     "downloads/ftp_file.txt"
        ... )

        Download from data URI:
        >>> result = download_web_file_from_url(
        ...     "data:text/plain;base64,SGVsbG8gV29ybGQ=",
        ...     "output.txt"
        ... )

        Download with custom timeout:
        >>> result = download_web_file_from_url(
        ...     "https://example.com/large-file.zip",
        ...     "downloads/large-file.zip",
        ...     timeout=60000
        ... )

    Notes:
        - Requires httpx library for HTTP/FTP downloads
        - Automatically creates parent directories if they don't exist
        - Returns absolute paths for consistency
        - Provides detailed error messages with stack traces on failure
        - Supports automatic content type detection for proper file handling
        - Handles both binary and text files appropriately
    """
    if not HTTPX_AVAILABLE:
        return (
            "Error: httpx is not installed. "
            "Install with: pip install 'fsc-assistant[web]'"
        )

    try:
        logger.debug(f"Downloading file from: {url} to: {destination}")

        # Parse URL to validate protocol
        parsed_url = urlparse(url)
        protocol = parsed_url.scheme.lower()

        # Validate protocol
        supported_protocols = ["http", "https", "ftp", "data"]
        if protocol not in supported_protocols:
            return (
                f"Error: Unsupported protocol '{protocol}'. "
                f"Supported protocols: {', '.join(supported_protocols)}"
            )

        # Resolve destination path
        dest_path = Path(destination).expanduser().resolve()

        # Create parent directories if they don't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Handle data URI separately
        if protocol == "data":
            return _download_data_uri(url, dest_path)

        # Handle FTP separately
        if protocol == "ftp":
            if not FTPLIB_AVAILABLE:
                return "Error: ftplib not available. FTP downloads are not supported."
            return _download_ftp(parsed_url, dest_path, timeout)

        # Handle HTTP/HTTPS with httpx
        return _download_http_https(url, dest_path, timeout)

    except Exception as e:
        error_msg = f"Error: Failed to download file - {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return error_msg


def _download_data_uri(data_uri: str, dest_path: Path) -> str:
    """
    Download file from a data URI.

    Args:
        data_uri: The data URI to decode
        dest_path: Path where the file will be saved

    Returns:
        str: Absolute path to the saved file

    Raises:
        ValueError: If the data URI is malformed
    """
    logger.debug(f"Processing data URI to: {dest_path}")

    # Parse data URI format: data:[<mediatype>][;charset=<charset>][;base64],<data>
    # More flexible pattern to handle various data URI formats
    pattern = r"^data:([^,]*?)(?:;(charset=[^,;]+))?(;base64)?,(.*)$"
    match = re.match(pattern, data_uri, re.DOTALL)

    if not match:
        # Fallback to simpler pattern for basic cases
        simple_pattern = r"^data:([^,]*)(;base64)?,(.*)$"
        match = re.match(simple_pattern, data_uri, re.DOTALL)
        if not match:
            raise ValueError(f"Malformed data URI: {data_uri[:100]}...")

    mime_type = match.group(1) or "text/plain"
    charset_match = match.group(2)
    is_base64 = (
        match.group(3) is not None
        if len(match.groups()) > 3
        else match.group(2) is not None
    )
    data = match.group(4) if len(match.groups()) > 3 else match.group(3)

    # Adjust if we used the simple pattern
    if len(match.groups()) <= 3:
        is_base64 = match.group(2) is not None
        data = match.group(3)

    # Decode data
    if is_base64:
        file_data = base64.b64decode(data)
        # Write binary data
        with open(dest_path, "wb") as f:
            f.write(file_data)
    else:
        # URL decode and write text
        import urllib.parse

        decoded_data = urllib.parse.unquote(data)
        # Try to detect encoding if charset is specified
        encoding = "utf-8"
        if charset_match and "charset=" in charset_match:
            encoding = charset_match.split("=")[1]

        with open(dest_path, "w", encoding=encoding) as f:
            f.write(decoded_data)

    logger.debug(f"Successfully saved data URI to: {dest_path}")
    return str(dest_path)


def _download_ftp(parsed_url, dest_path: Path, timeout: int) -> str:
    """
    Download file from FTP URL using ftplib.

    Args:
        parsed_url: Parsed URL object from urllib.parse.urlparse
        dest_path: Path where the file will be saved
        timeout: Maximum time in seconds to wait

    Returns:
        str: Absolute path to the saved file

    Raises:
        Exception: For FTP errors
    """
    logger.debug(f"Downloading from FTP: {parsed_url.geturl()} to: {dest_path}")

    if not FTPLIB_AVAILABLE:
        raise Exception("ftplib not available. FTP downloads are not supported.")

    try:
        # Extract FTP connection details
        host = parsed_url.hostname
        port = parsed_url.port or 21
        username = parsed_url.username or "anonymous"
        password = parsed_url.password or "anonymous@"
        path = parsed_url.path

        # Connect to FTP server
        ftp = ftplib.FTP()
        ftp.connect(host, port, timeout=timeout / 1000)
        ftp.login(username, password)

        # Download file
        with open(dest_path, "wb") as f:
            ftp.retrbinary(f"RETR {path}", f.write)

        ftp.quit()
        logger.debug(f"Successfully downloaded FTP file to: {dest_path}")
        return str(dest_path)

    except Exception as e:
        raise Exception(f"FTP download failed: {str(e)}")


def _download_http_https(url: str, dest_path: Path, timeout: int) -> str:
    """
    Download file from HTTP or HTTPS URL using httpx.

    Args:
        url: The URL to download from
        dest_path: Path where the file will be saved
        timeout: Maximum time in milliseconds to wait

    Returns:
        str: Absolute path to the saved file

    Raises:
        httpx.HTTPError: For HTTP/HTTPS errors
        Exception: For other download errors
    """
    logger.debug(f"Downloading from HTTP/HTTPS: {url} to: {dest_path}")

    # Determine if we should use binary mode based on file extension or content type
    # Default to binary for safety
    is_binary = True
    file_extension = dest_path.suffix.lower()

    # Common text file extensions
    text_extensions = {
        ".txt",
        ".csv",
        ".json",
        ".xml",
        ".html",
        ".htm",
        ".css",
        ".js",
        ".py",
        ".md",
        ".rst",
        ".yaml",
        ".yml",
        ".ini",
        ".cfg",
        ".conf",
        ".log",
        ".sh",
        ".bat",
        ".ps1",
    }

    if file_extension in text_extensions:
        is_binary = False

    # Download with httpx
    with httpx.Client(timeout=timeout / 1000, follow_redirects=True) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()

            # Check content type from headers if we haven't determined it's text
            if is_binary:
                content_type = response.headers.get("content-type", "").lower()
                if content_type.startswith("text/") or "charset" in content_type:
                    is_binary = False

            # Download and save file
            if is_binary:
                # Download in binary mode
                with open(dest_path, "wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)
            else:
                # Download as text with encoding detection
                content = response.read()

                # Try to detect encoding
                encoding = response.encoding or "utf-8"

                # If chardet is available, use it for better detection
                try:
                    import chardet

                    detected = chardet.detect(content)
                    if detected and detected["encoding"]:
                        encoding = detected["encoding"]
                except ImportError:
                    pass

                # Write text content
                text_content = content.decode(encoding, errors="replace")
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(text_content)

    logger.debug(f"Successfully downloaded to: {dest_path}")
    return str(dest_path)
