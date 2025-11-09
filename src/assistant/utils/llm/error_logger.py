import json
import os
from typing import Any, Dict, List


def get_timestamp_string() -> str:
    """Get the current timestamp as a formatted string."""
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d_%H%M%S")


def log_error(
    error_message: str, messages: List[Dict[str, Any]] = None, **kwargs
) -> str:
    """Log LLM error messages to a file for debugging and analysis."""
    if os.environ.get("DEBUG", "False").lower() != "true":
        return ""

    log_file = f"llm_error_log_{get_timestamp_string()}.txt"
    with open(log_file, "w") as log_fh:
        log_fh.write(error_message + "\n")
        params = {key: value for key, value in kwargs.items()}
        if messages:
            for msg in messages:
                log_fh.write(json.dumps(msg, indent=2) + "\n")
        if params:
            log_fh.write("Parameters:\n")
            log_fh.write(json.dumps(params, indent=2) + "\n")
    print(f"LLM error logged to {log_file}")
    return log_file
