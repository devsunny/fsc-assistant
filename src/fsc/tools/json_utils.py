import json
from datetime import datetime, date


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


def json_to_string(data, **kwargs) -> str:
    """Convert JSON data to a string with pretty printing and optional formatting options."""
    return json.dumps(data, cls=CustomJsonEncoder, indent=2, **kwargs)

def pretty_print_json(data, **kwargs) -> None:
    """Pretty print JSON data with optional formatting options."""
    print(json_to_string(data, **kwargs))

def save_json_to_file(data, file_path: str, **kwargs) -> None:
    """Save JSON data to a file with pretty printing and optional formatting options."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, cls=CustomJsonEncoder, indent=2, ensure_ascii=False, **kwargs)   

def load_json_from_file(file_path: str):
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f) 

