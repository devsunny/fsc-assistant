from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def get_current_local_time() -> str:
    """
    Get the current local date and time with timezone information.

    This function provides AI assistants with temporal awareness by returning
    the current date and time in multiple formats. This enables time-sensitive
    responses, accurate timestamp generation, and understanding of temporal
    context in user queries.

    Returns:
        str: Current local time in multiple formats:
             - ISO 8601 format with timezone offset
             - Timezone name and UTC offset
             - Human-readable format with day, date, and time

    Examples:
        Get current time information:
        >>> time_info = get_current_local_time()
        >>> print(time_info)
        Current local time: 2024-11-07T14:30:45.123456-05:00
        Timezone: EST (UTC-05:00)
        Human readable: Thursday, November 7, 2024 at 2:30:45 PM

        Use for timestamp generation:
        >>> time_info = get_current_local_time()
        >>> # Extract ISO format for logs
        >>> iso_time = time_info.split('\\n')[0].split(': ')[1]

        Use for temporal context:
        >>> time_info = get_current_local_time()
        >>> # AI can understand "today" means the date shown
        >>> if "Thursday" in time_info:
        ...     print("Today is Thursday")

    Notes:
        - Uses Python standard library only (no external dependencies)
        - Automatically detects local timezone
        - Handles Daylight Saving Time (DST) correctly
        - Executes in <10ms (no I/O or network calls)
        - Works consistently across all platforms (Linux, macOS, Windows)
        - Returns timezone-aware datetime information
    """
    try:
        # Get current time in local timezone
        now = datetime.now(tz=timezone.utc).astimezone()

        # Format ISO 8601 with timezone
        iso_format = now.isoformat()

        # Get timezone name and offset
        tz_name = now.strftime("%Z")
        tz_offset = now.strftime("%z")
        # Format offset as UTC±HH:MM
        tz_offset_formatted = f"{tz_offset[:3]}:{tz_offset[3:]}"

        # Human-readable format
        human_format = now.strftime("%A, %B %d, %Y at %I:%M:%S %p")

        return (
            f"Current local time: {iso_format}\n"
            f"Timezone: {tz_name} (UTC{tz_offset_formatted})\n"
            f"Human readable: {human_format}"
        )
    except Exception as e:
        logger.exception("Error getting current time")
        return f"Error: Failed to get current time - {str(e)}"
