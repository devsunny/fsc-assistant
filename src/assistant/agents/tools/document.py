"""Document conversion tools using Docling.

Provides functions to convert non-text documents (PDF, DOCX, PPTX, etc.)
into Markdown format using the Docling library.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Union

# Suppress TensorFlow warnings before importing docling
# Docling uses TensorFlow internally for document processing
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')  # 0=all, 1=info, 2=warning, 3=error

from docling.document_converter import DocumentConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_document_to_markdown(
    input_path: Union[str, Path], output_path: Union[str, Path]
) -> str:
    """Convert a document to Markdown format."""
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    try:
        # Initialize Docling converter
        converter = DocumentConverter()
        # Convert the document
        result = converter.convert(input_path)
        # Export to Markdown
        markdown_content = result.document.export_to_markdown()

        output_path = Path(output_path)
        output_path.write_text(markdown_content, encoding="UTF-8")

        return f"Converted document saved to {output_path}"
    except Exception as e:
        return f"Failed to convert document: {e!r}"


def extract_table_from_document_to_markdown(
    input_path: Union[str, Path], output_path: Union[str, Path], table_index: int = 0
) -> str:
    """Extract a specific table from a document and return it as Markdown."""
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    try:
        converter = DocumentConverter()
        result = converter.convert(input_path)
        tables = result.document.get_tables()
        if table_index < 0 or table_index >= len(tables):
            return f"Table index {table_index} out of range. Document has {len(tables)} tables."

        table_md = tables[table_index].export_to_markdown()
        output_path = Path(output_path)
        output_path.write_text(table_md, encoding="UTF-8")
        return f"extracted tables saved to {output_path}"
    except Exception as e:
        logger.exception("Error extracting table from document", exc_info=e)
        return f"Failed to extract tables: {e!r}"


def extract_all_tables_from_document_to_markdown(
    input_path: Union[str, Path], output_path: Union[str, Path]
) -> str:
    """Extract all tables from a document and return them as Markdown."""
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    try:
        converter = DocumentConverter()
        result = converter.convert(input_path)
        tables = result.document.get_tables()
        if not tables:
            return "No tables found in the document."

        all_tables_md = "\n\n".join(table.export_to_markdown() for table in tables)
        output_path = Path(output_path)
        output_path.write_text(all_tables_md, encoding="UTF-8")
        return f"extracted tables saved to {output_path}"
    except Exception as e:
        logger.exception("Error extracting tables from document", exc_info=e)
        return f"Failed to extract tables: {e!r}"
