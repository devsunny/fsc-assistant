import logging
from typing import List, Union
from pathlib import Path

from assistant.utils.llm.img_utils import to_multipart_message_content


logger = logging.getLogger(__name__)


def load_image_files_from_disk(image_filepaths: List[str]) -> str:
    """load multiple image files from disk"""
    content = to_multipart_message_content(*image_filepaths)
    logger.info(f"Loaded {len(image_filepaths)} image files from disk.")
    return content


def save_binary_file_to_disk(path: Union[str, Path], content: bytes) -> str:
    """Save binary CONTENT to a file at PATH (create directories if needed). Returns the absolute path."""
    try:
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return f"Saved to {p}"
    except Exception as e:
        return f"Failed to save file: {e!r}"
