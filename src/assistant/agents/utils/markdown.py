# Requires: pathlib

"""
Module for extracting code blocks from markdown content and saving them to files.
"""

import io
import re
from pathlib import Path
from typing import List, Optional, Tuple

import click


class MarkdownCodeExtractor:
    """Extract code blocks from markdown content and save to files."""

    def __init__(self):
        """Initialize the MarkdownCodeExtractor."""
        self.filename_pattern = re.compile(
            r"^###\s+Filename:\s+(.+?)(?:\n|$)", re.IGNORECASE
        )
        self.code_block_start = re.compile(r"^```[a-zA-Z][a-zA-Z0-9]+$")
        self.code_block_end = re.compile(r"^```$")

    def extract_code_blocks(self, markdown_content: str) -> List[Tuple[str, str]]:
        """
        Extract code blocks with their associated filenames from markdown content.

        Args:
            markdown_content: The markdown content to parse

        Returns:
            List of tuples containing (filename, code_content)
        """
        in_code_block = False
        filename = None
        code_buffer = []
        nested = 0
        code_blocks = []
        fund_readme = False
        code_line_num = 0

        for line in io.StringIO(markdown_content):
            filename_match = self.filename_pattern.search(line.rstrip())
            code_start_match = self.code_block_start.search(line.rstrip())
            code_end_match = self.code_block_end.search(line.rstrip())
            if filename_match and filename is None:
                filename = filename_match.group(1)
                fund_readme = filename == "README.md"
            elif code_start_match and in_code_block is False:
                in_code_block = True
            elif code_start_match and in_code_block is True:
                code_line_num += 1
                nested += 1
                if fund_readme is True:
                    print(line.rstrip())
                code_buffer.append(line)
            elif code_end_match and nested > 0 and in_code_block is True:
                code_line_num += 1
                nested -= 1
                if fund_readme is True:
                    print(line.rstrip())
                code_buffer.append(line)
            elif code_end_match and nested == 0 and in_code_block is True:
                code_block = "".join(code_buffer)
                code_blocks.append((filename, code_block))
                fund_readme = False
                filename = None
                code_buffer = []
                in_code_block = False
                nested = 0
            elif in_code_block is True:
                code_line_num += 1
                if (
                    code_line_num == 1
                    and line.rstrip().startswith("// ")
                    and filename is None
                ):
                    filename = line.rstrip()[3:].strip()
                else:
                    code_buffer.append(line)

                if fund_readme is True:
                    print(line.rstrip())

        return code_blocks

    def save_to_files(
        self,
        code_blocks: List[Tuple[str, str]],
        base_directory: Optional[str] = None,
        is_test: bool = False,
    ) -> List[str]:
        """
        Save extracted code blocks to their respective files.

        Args:
            code_blocks: List of tuples containing (filename, code_content)
            base_directory: Base directory for saving files (default: current directory)

        Returns:
            List of created file paths
        """
        created_files = []
        base_path = Path(base_directory) if base_directory else Path.cwd()

        for filename, content in code_blocks:
            if is_test and base_path.name == "tests" and filename.startswith("tests/"):
                base_path = base_path.parent

            file_path = base_path / filename
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            # Write content to file
            file_path.write_text(content, encoding="utf-8")
            created_files.append(str(file_path))

        return created_files

    def analyze_and_extract(
        self,
        markdown_content: str,
        base_directory: Optional[str] = None,
        is_test: bool = False,
    ) -> List[str]:
        """
        Analyze markdown content and extract code blocks to files.

        Args:
            markdown_content: The markdown content to analyze
            base_directory: Base directory for saving files (default: current directory)

        Returns:
            List of created file paths
        """
        code_blocks = self.extract_code_blocks(markdown_content)
        return self.save_to_files(code_blocks, base_directory, is_test)


def extract_markdown_code_blocks(
    markdown_content: str,
    base_directory: Optional[str] = None,
    is_test: bool = False,
) -> List[str]:
    """
    Extract code blocks from markdown content and save them to files.

    Args:
        markdown_content: The markdown content containing code blocks
        base_directory: Base directory for saving files (default: current directory)

    Returns:
        List of created file paths
    """
    extractor = MarkdownCodeExtractor()
    return extractor.analyze_and_extract(markdown_content, base_directory, is_test)


@click.command()
@click.option(
    "--input-md",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path to the input mardownfile file",
)
@click.option(
    "--output-folder",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    help="Directory to save the code files",
)
def main(input_md, output_folder):
    """extract markdown code block to files."""

    try:
        with open(input_md, "rt", encoding="utf-8") as fin:
            content = fin.read()

        output_folder = output_folder if output_folder else Path.cwd()
        output_files = extract_markdown_code_blocks(content, output_folder)
    except Exception as e:
        click.echo(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
