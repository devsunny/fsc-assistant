from rich import box
from rich.console import Console
from rich.panel import Panel
from .__version__ import __version__


def render_assistant_banner() -> None:
    """
    Render and display the FSC Assistant banner in the terminal.
    """
    banner_str = generate_fsc_ascii(color=True, wide=True, show_openspec=True)
    print(banner_str)


def generate_fsc_ascii(
    *, color: bool = True, wide: bool = True, show_openspec: bool = True
) -> str:
    """
    Generate an ASCII banner for the supervised Full AI self-coding "FSC Assistant",
    visually themed to emphasize tight integration with the OpenSpec GitHub project.

    Args:
        color (bool): If True, wrap the banner with ANSI colors (works in most terminals).
        wide (bool): If True, render a wide, framed banner; otherwise a compact one-liner.
        show_openspec (bool): If True, include an integration strip referencing OpenSpec.

    Returns:
        str: The ASCII art banner.
    """
    # ANSI palette (kept subtle for legibility). Turn off with color=False.
    RESET = "\x1b[0m"
    DIM = "\x1b[2m"
    BRIGHT = "\x1b[1m"
    CYAN = "\x1b[36m"
    GREEN = "\x1b[32m"
    MAGENTA = "\x1b[35m"
    YELLOW = "\x1b[33m"

    def tint(s, c):
        return f"{c}{s}{RESET}" if color else s

    if wide:
        top = "┌" + "─" * 80 + "┐"
        bot = "└" + "─" * 80 + "┘"
        title_line_1 = (
            "|               "
            f"{tint('<', CYAN)}{tint('/', CYAN)}{tint('>', CYAN)}  "
            f"{tint('{', GREEN)}{tint('}', GREEN)}  "
            f"{tint('(', MAGENTA)}{tint(')', MAGENTA)}  "
            f"{tint('[', YELLOW)}{tint(']', YELLOW)}   "
            f"{tint('FSC ASSISTANT', BRIGHT)}"
            f"{tint('   [', YELLOW)}{tint(']', YELLOW)}   "
            f"{tint('(', MAGENTA)}{tint(')', MAGENTA)}  "
            f"{tint('{', GREEN)}{tint('}', GREEN)}  "
            f"{tint('<', CYAN)}{tint('/', CYAN)}{tint('>', CYAN)}   " + " " * 12 + "│"
        )
        title_line_2 = (
            "│    Supervised • Full AI • Self-Coding  "
            "— tightly integrated with OpenSpec      │"
        )
        # Stylized “core” line hinting at a build/test/ship pipeline
        core = (
            "│         pipeline:  parse ⇢ plan ⇢ write ⇢ test ⇢ review ⇢ ship "
            + " " * 16
            + "│"
        )
        # “Chip”/“brain” block logo
        logo = [
            "│               ╭──────────╮    ╭──────────╮    ╭─────────────╮"
            + " " * 18
            + "│",
            f"│               │  {tint('FS', BRIGHT)} 01   │    │  {tint('SC', BRIGHT)} 02   │    │  {tint('AI', BRIGHT)} 03      │"
            + " " * 18
            + "│",
            "│               │  self-   │    │  coder   │    │  supervised │"
            + " " * 18
            + "│",
            "│               │  wiring  │    │  tests   │    │  reviews    │"
            + " " * 18
            + "│",
            "│               ╰──────────╯    ╰──────────╯    ╰─────────────╯"
            + " " * 18
            + "│",
        ]
        openspec = (
            "│  integration: OpenSpec ▸ spec ⇢ constraints ⇢ scaffolds ⇢ checks"
            + " " * 15
            + "│"
            if show_openspec
            else "│                                                                   │"
        )
        repo_hint = (
            f"│  {tint('github.com/openspec', DIM)}" + " " * 59 + "│"
            if show_openspec
            else "│                                                                   │"
        )
        # Bottom cadence line
        cadence = "│  <code/>  {config}  (orchestrate)  [validate]" + " " * 34 + "│"

        lines = [
            top,
            title_line_1,
            title_line_2,
            core,
            *logo,
            openspec,
            repo_hint,
            cadence,
            bot,
        ]
        return "\n".join(lines)

    # Compact version (single block)
    compact = (
        f"{tint('┏━━━━━━━━ FSC Assistant ━━━━━━━━┓', BRIGHT)}\n"
        f"{tint('┃ Supervised • Full AI • Self-Coding ┃', DIM)}\n"
        f"{tint('┃ <code/> {config} (orchestrate) [validate] ┃', CYAN)}\n"
        + (
            f"{tint('┃ OpenSpec-integrated: specs ⇢ scaffolds ⇢ checks ┃', GREEN)}\n"
            if show_openspec
            else ""
        )
        + f"{tint('┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛', BRIGHT)}"
    )
    return compact


# --- Example usage ---
if __name__ == "__main__":
    print(generate_fsc_ascii(color=True, wide=True, show_openspec=True))
    # For a simpler banner:
    # print(generate_fsc_ascii(color=False, wide=False, show_openspec=False))
