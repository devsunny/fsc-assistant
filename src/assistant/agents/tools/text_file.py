from pathlib import Path
from assistant.utils.json import CustomJsonEncoder
import json

def save_text_file_to_disk(path: str, content: str) -> str:
    """Save text CONTENT to a file at PATH (create directories if needed). Returns the absolute path."""
    try:
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        if content and not isinstance(content, str):
            try:
                content = json.dumps(content, indent=2, cls=CustomJsonEncoder)
            except Exception:
                content = str(content)                        
        p.write_text(content, encoding="utf-8")
        return f"Saved to {p}"
    except Exception as e:
        return f"Failed to save file: {e!r}"


def load_text_file_from_disk(path: str) -> str:
    """Load and return the text contents of the file at PATH."""
    try:
        p = Path(path).expanduser().absolute()
        if not p.exists():
            return f"File not found: {p}"
        # Basic guard against very large files in CLI
        if p.stat().st_size > 5 * 1024 * 1024:
            return f"File too large to display (>5MB): {p}"
        data = p.read_text(encoding="utf-8", errors="ignore")
        return data
    except Exception as e:
        return f"Failed to load file: {e}"
