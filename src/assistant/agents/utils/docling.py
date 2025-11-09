import os
from pathlib import Path

import click

# Suppress TensorFlow warnings before importing docling
# Docling uses TensorFlow internally for document processing
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')  # 0=all, 1=info, 2=warning, 3=error

from docling.document_converter import DocumentConverter


@click.command
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
    required=True,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=False, dir_okay=False, file_okay=True, path_type=Path),
)
def main(input: Path, output: Path = None):
    if output is None:
        output = input.parent / (input.name + ".md")

    converter = DocumentConverter()
    result = converter.convert(input)
    md = result.document.export_to_markdown()
    output.write_text(md)


if __name__ == "__main__":
    main()
