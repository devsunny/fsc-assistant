import os
from pathlib import Path
from typing import Dict, List, Optional, Union

# Constants: File extension to programming language mapping
FILE_EXTENSION_TO_LANGUAGE: Dict[str, str] = {
    # Python
    ".py": "python",
    ".pyw": "python",
    ".pyx": "python",
    ".pyi": "python",
    # JavaScript/TypeScript
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    # Web
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    # Java/Kotlin
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    # C/C++
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".hh": "cpp",
    ".hxx": "cpp",
    # C#
    ".cs": "csharp",
    ".csx": "csharp",
    # Go
    ".go": "go",
    # Rust
    ".rs": "rust",
    # Ruby
    ".rb": "ruby",
    ".erb": "erb",
    # PHP
    ".php": "php",
    ".phtml": "php",
    # Swift
    ".swift": "swift",
    # Objective-C
    ".m": "objectivec",
    ".mm": "objectivec",
    # Shell
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".fish": "fish",
    ".ps1": "powershell",
    ".psm1": "powershell",
    # SQL
    ".sql": "sql",
    # R
    ".r": "r",
    ".R": "r",
    # MATLAB
    ".m": "matlab",
    ".mat": "matlab",
    # Scala
    ".scala": "scala",
    ".sc": "scala",
    # Lua
    ".lua": "lua",
    # Perl
    ".pl": "perl",
    ".pm": "perl",
    # Haskell
    ".hs": "haskell",
    ".lhs": "haskell",
    # Clojure
    ".clj": "clojure",
    ".cljs": "clojure",
    ".cljc": "clojure",
    # Elixir
    ".ex": "elixir",
    ".exs": "elixir",
    # Erlang
    ".erl": "erlang",
    ".hrl": "erlang",
    # Julia
    ".jl": "julia",
    # Dart
    ".dart": "dart",
    # F#
    ".fs": "fsharp",
    ".fsi": "fsharp",
    ".fsx": "fsharp",
    # Visual Basic
    ".vb": "vbnet",
    ".vbs": "vbscript",
    # VUE3
    ".vue": "vue3",
    # Assembly
    ".asm": "assembly",
    ".s": "assembly",
    # YAML/JSON/XML
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".xml": "xml",
    ".toml": "toml",
    ".ini": "ini",
    # Markdown
    ".md": "markdown",
    ".markdown": "markdown",
    # Docker
    ".dockerfile": "dockerfile",
    # Make
    ".mk": "makefile",
    # CMake
    ".cmake": "cmake",
    # Gradle
    ".gradle": "gradle",
    # Maven
    ".pom": "xml",
}


def is_hidden(path: Path) -> bool:
    """
    Check if a file or directory is hidden.

    Args:
        path: Path object to check

    Returns:
        True if the path is hidden, False otherwise
    """
    # Check if any part of the path starts with a dot (hidden)
    for part in path.parts:
        if part.startswith(".") and part != ".":
            return True
    return False


def is_source_file(file_path: Path) -> bool:
    """
    Check if a file is a programming language source file.

    Args:
        file_path: Path object of the file to check

    Returns:
        True if the file is a source file, False otherwise
    """
    return file_path.suffix.lower() in FILE_EXTENSION_TO_LANGUAGE


def get_language_for_extension(extension: str) -> str:
    """
    Get the programming language for a file extension.

    Args:
        extension: File extension (e.g., '.py')

    Returns:
        Programming language name for markdown code blocks
    """
    return FILE_EXTENSION_TO_LANGUAGE.get(extension.lower(), "text")


def read_file_content(file_path: Path) -> Optional[str]:
    """
    Read the content of a file safely.

    Args:
        file_path: Path object of the file to read

    Returns:
        File content as string, or None if reading fails
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, PermissionError, IOError) as e:
        print(f"Warning: Could not read file {file_path}: {e}")
        return None


def format_file_in_markdown(
    file_path: Path, base_path: Optional[Path] = None
) -> Optional[str]:
    """
    Format a single source file in markdown format.

    Args:
        file_path: Path object of the file to format
        base_path: Optional base path for relative path display

    Returns:
        Formatted markdown string, or None if file cannot be processed
    """
    content = read_file_content(file_path)
    if content is None:
        return None

    # Get the display path (relative to base_path if provided)
    if base_path:
        try:
            display_path = file_path.relative_to(base_path)
        except ValueError:
            display_path = file_path
    else:
        display_path = file_path

    # Convert Path to string with forward slashes for consistency
    display_path_str = str(display_path).replace("\\", "/")

    # Get the programming language for syntax highlighting
    language = get_language_for_extension(file_path.suffix)

    # Format in markdown
    markdown = f"## {display_path_str}\n"
    markdown += f"```{language}\n"
    markdown += content
    if not content.endswith("\n"):
        markdown += "\n"
    markdown += "```\n\n"

    return markdown


def collect_source_files(path: Path) -> List[Path]:
    """
    Collect all source files from a path (file or directory).

    Args:
        path: Path object (can be file or directory)

    Returns:
        List of Path objects for all source files found
    """
    source_files = []

    if path.is_file():
        # Single file
        if not is_hidden(path) and is_source_file(path):
            source_files.append(path)
    elif path.is_dir():
        # Directory - walk recursively
        for root, dirs, files in os.walk(path):
            root_path = Path(root)

            # Skip hidden directories
            if is_hidden(root_path):
                continue

            # Filter out hidden directories from further traversal
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            # Process files in current directory
            for file in files:
                file_path = root_path / file

                if not is_hidden(file_path) and is_source_file(file_path):
                    source_files.append(file_path)

    # Sort files for consistent output
    source_files.sort()
    return source_files


def concatenate_source_files(
    path: Union[Path, str], output_file: Optional[str] = None
) -> str:
    """
    Read source code files and concatenate them in markdown format.

    This function handles both single files and directories recursively,
    ignoring hidden files/folders and non-programming language files.

    Args:
        path: Path to a file or directory to process
        output_file: Optional path to save the output markdown file

    Returns:
        Concatenated markdown string of all source files

    Example:
        >>> result = concatenate_source_files("./src")
        >>> print(result)
        ## src/main.py
        ```python
        print("Hello, World!")
        ```

        ## src/utils/helper.js
        ```javascript
        function helper() { return true; }
        ```
    """
    input_path = Path(path).resolve() if isinstance(path, str) else path

    if not input_path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")
    # Collect all source files
    source_files = collect_source_files(input_path)

    if not source_files:
        return "No source files found in the specified path."

    # Determine base path for relative path display
    base_path = input_path.parent if input_path.is_file() else input_path

    # Concatenate all files in markdown format
    markdown_content = ""
    processed_count = 0

    for file_path in source_files:
        formatted = format_file_in_markdown(file_path, base_path)
        if formatted:
            markdown_content += formatted
            processed_count += 1

    # Add summary at the beginning
    summary = f"# Source Code Files\n\n"
    summary += f"Total files processed: {processed_count}\n\n"
    summary += "---\n\n"

    final_content = summary + markdown_content

    # Save to file if output_file is specified
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"Output saved to: {output_file}")

    return final_content


# Example usage
if __name__ == "__main__":
    # Example 1: Process a single file
    # result = concatenate_source_files("example.py")

    # Example 2: Process a directory recursively
    # result = concatenate_source_files("./src")

    # Example 3: Process and save to file
    # result = concatenate_source_files("./project", "output.md")

    # Example 4: Process current directory
    result = concatenate_source_files(".", "source_code_output.md")
    print(f"Processing complete. Check the output file or use the returned string.")
