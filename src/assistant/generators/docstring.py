import json
import os
import time
from io import StringIO

import click
from yaspin import yaspin
from yaspin.spinners import Spinners

from ..llm.client import LLMClient


@click.command
@click.argument(
    "file_path",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
)
def generate_docstring(file_path: click.Path = None):
    """this function generate python docstring"""
    sp = yaspin(Spinners.earth, text="")
    sp.start()
    try:
        _ai_generate_docstring(file_path)
    finally:
        try:
            time.sleep(1)
        except Exception:
            pass
        sp.stop()


def _ai_generate_docstring(file_path: click.Path = None):
    """this function generate python docstring"""
    if file_path is None:
        return

    with open(file_path, "r", encoding="utf-8") as fin:
        python_source_code = fin.read()

    prompt = f'''You are an expert Python developer. Your task is to analyze the provided Python source code and generate a comprehensive docstring for each class, method, module, and function that is missing one.

The docstrings must follow the Google Style Python Docstrings format.

Your final output should be the full Python file content, with the newly generated docstrings inserted into the correct locations. Do not provide any additional explanation or conversational text, just the code.

For functions and methods, the docstrings must include:
* A concise, one-line summary.
* A more detailed description (optional, if needed).
* A `Args` section that describes each parameter, including its type and purpose.
* A `Returns` section that describes what the function returns and its type.
* A `Raises` section for any exceptions the function might raise.

For classes, the docstrings must include:
* A concise, one-line summary.
* A detailed description of the class's purpose and its attributes.

For modules (at the top of the file), the docstrings must include:
* A description of the module's overall purpose and what it contains.

output python source with updated docstring, no commentary, notes and explanation

Here is an example of the desired format for a function:

[BEGIN EXAMPLE CODE]
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers.

    This function takes two integers and returns their sum.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of `a` and `b`.
    """
    return a + b
[END EXAMPLE CODE]

Now, analyze the following Python source code and generate the appropriate docstrings.

```python
{python_source_code}
```
'''
    llm = LLMClient()
    response_text = ""
    for chunk in llm.invoke_model_generator(prompt):
        response_text += chunk
        print(chunk, end="", flush=True)

    lines = StringIO(response_text)
    codes = []
    for line in lines:
        if line.startswith("```"):
            pass
        else:
            codes.append(line)

    with open(file_path, "wt", encoding="utf-8") as fout:
        fout.write("".join(codes))
        # end overwrite file

    print(f"python code is written to {file_path}")
