import signal
from pathlib import Path
from typing import Literal, Optional

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit import print_formatted_text as console_print
from prompt_toolkit.history import FileHistory

COLORS = [
    "ansiblack",
    "ansired",
    "ansigreen",
    "ansiyellow",
    "ansiblue",
    "ansimagenta",
    "ansicyan",
    "ansigray",
    "ansibrightblack",
    "ansibrightred",
    "ansibrightgreen",
    "ansibrightyellow",
    "ansibrightblue",
    "ansibrightmagenta",
    "ansibrightcyan",
    "ansiwhite",
]


class CLIConsole:
    def __init__(self):
        assistant_hist = Path.home() / ".assistant/.kara_prompt_history"
        if assistant_hist.exists() is False:
            assistant_hist.parent.mkdir(exist_ok=True)
            assistant_hist.write_text("")
        self.prompt_history = FileHistory(assistant_hist.resolve())
        self.prompt_session = PromptSession(history=self.prompt_history)

    def get_multiline_input(
        self, input_prompt: str = "Enter your prompt"
    ) -> Optional[str]:
        """Get multi-line input from user"""
        console_print(
            HTML(
                f"<ansicyan><b>{input_prompt} (double Enter to submit):</b></ansicyan>"
            )
        )
        lines = []
        try:
            line_pos = 0
            while True:
                line_pos += 1
                if line_pos == 1:
                    line = self.prompt_session.prompt(
                        HTML("<ansiyellow>[You]&gt;&gt;&gt; </ansiyellow>")
                    )
                else:
                    line = self.prompt_session.prompt(
                        HTML("<ansiyellow>... </ansiyellow>")
                    )

                if (
                    len(lines) == 1
                    and lines[0].strip() in ["quit", "exit", "bye", "\\q"]
                    and line == ""
                ):
                    break
                elif line == "" and lines and lines[-1] == "":
                    lines.pop()  # Remove the last empty line
                    break
                lines.append(line)
                
                #signal.CTRL_BREAK_EVENT

        except KeyboardInterrupt:
            console_print(HTML(f"<ansiyellow>Input cancelled</ansiyellow>"))
            return None

        prompt = "\n".join(lines).strip()
        return prompt if prompt else None

    def prompt_input(self, input_prompt: str = "Enter your prompt") -> str:
        console_print(
            HTML(f"<ansicyan><b>{input_prompt}(Enter to submit):</b></ansicyan>")
        )
        line = self.prompt_session.prompt(
            HTML(f"<ansiyellow>&gt;&gt;&gt;</ansiyellow>")
        )
        return line.strip() if line else ""

    def print(
        self,
        message,
        color: Literal[
            "black",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "gray",
            "brightblack",
            "brightred",
            "brightgreen",
            "brightyellow",
            "brightblue",
            "brightmagenta",
            "brightcyan",
            "white",
        ] = None,
        style: Literal["b", "i"] = None,
        end="\n",
    ) -> None:
        ansicolor = f"ansi{color}" if not color.startswith("ansi") else color
        prompt = message
        if style in ["b", "i"]:
            prompt = f"<{style}>{prompt}</{style}>"
        if ansicolor in COLORS:
            prompt = f"<{ansicolor}>{prompt}</{ansicolor}>"
        console_print(HTML(prompt), end=end)


# Lazy loading singleton instance
_cli_console_instance = None

def get_cli_console() -> CLIConsole:
    """Get the singleton instance of CLIConsole, creating it if needed."""
    global _cli_console_instance
    if _cli_console_instance is None:
        _cli_console_instance = CLIConsole()
    return _cli_console_instance
