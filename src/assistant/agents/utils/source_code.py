# file_manager_rich.py
# Requires: rich

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

console = Console()


TOOL_CONFIGS = {
    "tools": [
        {
            "toolSpec": {
                "name": "save_to_file",
                "description": "Saves the given content to the specified file path. Returns file name on success, error message on error.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file to save.",
                            },
                            "file_content": {
                                "type": "string",
                                "description": "The content to write to the file.",
                            },
                        },
                        "required": ["file_path", "file_content"],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "read_file",
                "description": "Reads the content of the source code file at the given path and returns it as a string.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The path to the file to read.",
                            }
                        },
                        "required": ["file_path"],
                    }
                },
            }
        },
    ]
}


class OperationCancelException(Exception):
    pass


def save_to_file(file_path: str, file_content: str) -> Optional[str]:
    """
    Save text content to a file with interactive options if file exists.

    Args:
        file_path (str): The path where the file should be saved.
        file_content (str): The content to write to the file.

    Returns:
        Optional[str]: The path where the file was saved, or None if cancelled.
    """
    file_path = Path(file_path)

    if file_path.exists():
        console.print(f"\n⚠️  [yellow]File '{file_path}' already exists![/yellow]")

        table = Table(title="[bold cyan]Choose an option[/bold cyan]")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")

        table.add_row("1", "Overwrite the existing file")
        table.add_row("2", "Save with auto-generated sequence number")
        table.add_row("3", "Cancel the operation")

        console.print(table)

        choice = Prompt.ask(
            "\n[bold]Enter your choice[/bold]", choices=["1", "2", "3"], default="3"
        )

        if choice == "1":
            if Confirm.ask(
                f"[bold red]Are you sure you want to overwrite '{file_path}'?[/bold red]"
            ):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("[cyan]Overwriting file...", total=None)
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(file_content)
                        progress.update(task, completed=True)
                        console.print(
                            f"✅ [bold green]File overwritten successfully:[/bold green] "
                            f"[cyan]{file_path}[/cyan]"
                        )
                        return str(file_path)
                    except IOError as ioe:
                        raise ioe
                    except Exception as e:
                        console.print(f"❌ [bold red]Error:[/bold red] {str(e)}")
                        raise IOError("failed to save file", e)
            else:
                console.print("❌ [yellow]Operation cancelled[/yellow]")
                raise OperationCancelException("Operation cancelled")

        elif choice == "2":
            base_path = file_path.parent
            base_name = file_path.stem
            extension = file_path.suffix

            counter = 1
            new_path = base_path / f"{base_name}_{counter:03d}{extension}"

            while new_path.exists():
                counter += 1
                new_path = base_path / f"{base_name}_{counter:03d}{extension}"

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"[cyan]Saving as '{new_path.name}'...", total=None
                )
                try:
                    with open(new_path, "w", encoding="utf-8") as f:
                        f.write(file_content)
                    progress.update(task, completed=True)
                    console.print(
                        f"✅ [bold green]File saved successfully:[/bold green] "
                        f"[cyan]{new_path}[/cyan]"
                    )
                    return str(new_path)
                except IOError as ioe:
                    raise ioe
                except Exception as e:
                    console.print(f"❌ [bold red]Error:[/bold red] {str(e)}")
                    raise IOError("failed to save file", e)
        else:
            console.print("❌ [yellow]Operation cancelled[/yellow]")
            return "Operation cancelled"
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Saving file...", total=None)
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_content)
                progress.update(task, completed=True)
                console.print(
                    f"✅ [bold green]File saved successfully:[/bold green] "
                    f"[cyan]{file_path}[/cyan]"
                )
                return str(file_path)
            except IOError as ioe:
                raise ioe
            except Exception as e:
                console.print(f"❌ [bold red]Error:[/bold red] {str(e)}")
                raise IOError("failed to save file", e)


def read_file(
    file_name: str, show_preview: bool = False
) -> Tuple[Optional[str], Optional[str]]:
    """
    Read a file with intelligent search capabilities and optional preview.

    Args:
        file_name (str): The name of the file to read.
        show_preview (bool): Whether to show a preview of the file content.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple of (file_content, file_path)
                                              or (None, None) if cancelled.
    """
    current_dir = Path.cwd()
    direct_path = current_dir / file_name

    if direct_path.exists() and direct_path.is_file():
        console.print(
            f"📁 [green]Found file in current directory:[/green] [cyan]{direct_path}[/cyan]"
        )
        selected_path = direct_path
    else:
        console.print(
            f"🔍 [yellow]File not found in current directory. "
            f"Searching subdirectories...[/yellow]"
        )

        found_files = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Searching for '{file_name}'...", total=None
            )

            for root, dirs, files in os.walk(current_dir):
                for file in files:
                    if file == file_name:
                        found_files.append(Path(root) / file)

            progress.update(task, completed=True)

        if not found_files:
            console.print(f"❌ [bold red]File '{file_name}' not found![/bold red]")
            return None, None

        if len(found_files) == 1:
            console.print(
                f"📁 [green]Found file:[/green] [cyan]{found_files[0]}[/cyan]"
            )
            selected_path = found_files[0]
        else:
            console.print(
                f"📝 [bold cyan]Found {len(found_files)} files with name "
                f"'{file_name}'[/bold cyan]"
            )

            table = Table(title="[bold]Select a file[/bold]")
            table.add_column("#", style="cyan", no_wrap=True)
            table.add_column("Relative Path", style="white")
            table.add_column("Size", style="green", no_wrap=True)
            table.add_column("Last Modified", style="yellow")

            for idx, file_path in enumerate(found_files, 1):
                rel_path = file_path.relative_to(current_dir)
                file_size = file_path.stat().st_size

                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                else:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"

                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                table.add_row(str(idx), str(rel_path), size_str, mod_time)

            console.print(table)

            choice = Prompt.ask(
                "\n[bold]Enter file number (or 'c' to cancel)[/bold]", default="c"
            )

            if choice.lower() == "c":
                console.print("❌ [yellow]Operation cancelled[/yellow]")
                return None, None

            try:
                file_idx = int(choice) - 1
                if 0 <= file_idx < len(found_files):
                    selected_path = found_files[file_idx]
                else:
                    console.print("❌ [red]Invalid selection![/red]")
                    return None, None
            except ValueError:
                console.print("❌ [red]Invalid input![/red]")
                return None, None

    try:
        with open(selected_path, "r", encoding="utf-8") as f:
            content = f.read()

        if show_preview:
            lines = content.split("\n")[:10]
            preview_content = "\n".join(lines)

            if selected_path.suffix in [".py", ".pyw"]:
                syntax = Syntax(
                    preview_content, "python", theme="monokai", line_numbers=True
                )
            else:
                syntax = Syntax(
                    preview_content, "text", theme="monokai", line_numbers=True
                )

            panel = Panel(
                syntax,
                title=f"[bold cyan]Preview: {selected_path.name}[/bold cyan]",
                subtitle="[dim]First 10 lines[/dim]",
                border_style="cyan",
            )
            console.print(panel)

        console.print(
            f"✅ [bold green]File loaded successfully:[/bold green] "
            f"[cyan]{selected_path}[/cyan]"
        )
        return content, str(selected_path)

    except IOError as ioe:
        raise ioe
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {str(e)}")
        raise IOError("failed to save file", e)


if __name__ == "__main__":
    import json

    save_to_file("tools.json", json.dumps(TOOL_CONFIGS, indent=2))
