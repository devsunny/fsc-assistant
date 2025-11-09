import json
from datetime import date, datetime


class CustomJsonEncoder(json.JSONEncoder):
    """
    A custom JSONEncoder that handles datetime.date and datetime.datetime objects
    by converting them to ISO 8601 strings.
    Other non-serializable objects are converted to a dictionary representation.
    """

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        try:
            # Attempt to convert other non-serializable objects to a dictionary
            return obj.__dict__
        except AttributeError:
            # If __dict__ is not available, fall back to the default JSONEncoder behavior
            return super().default(obj)


def extract_json_from_text(text: str) -> str:
    """
    Extracts the JSON object from a given text string.
    The JSON object is expected to be enclosed within the first pair of curly braces {}.

    Args:
        text (str): The input text containing a JSON object.

    Returns:
        str: The extracted JSON string, or an empty string if no valid JSON is found.
    """
    start_idx = text.find("{")
    end_idx = text.rfind("}")

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = text[start_idx : end_idx + 1]
        try:
            # Validate if the extracted string is a valid JSON
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            return ""
    return ""
