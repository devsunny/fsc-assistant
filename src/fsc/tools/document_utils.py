import logging
from pathlib import Path
from typing import Union
from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)    

def read_document(input_path: Union[Path, str]) -> str:
    """Reads a document from the given input path or url and returns its markdown text content."""
    try:
        converter = DocumentConverter()   
        doc = converter.convert(input_path).document
        return doc.export_to_markdown()
    except Exception as e:
        logger.exception(e)
        logger.error(f"Failed to read document from {input_path}: {e}")
        return f"Failed to read document from {input_path}: {e}"