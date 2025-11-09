import json
import os
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional

import click

from ..agents.utils.markdown import extract_markdown_code_blocks
from ..llm.client import llmclient
from ..prompts.vue import VUE_UNITTEST_PROMPT
from ..utils.source_code import concatenate_source_files


def read_text_file(file_path):
    if file_path is None or os.path.exists(file_path) is False:
        return "Empty file"
    with open(file_path, "rt", encoding="utf-8") as fin:
        return fin.read()


@click.command
@click.argument(
    "vue3files",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
    nargs=-1,
)
@click.option(
    "--output-dir",
    "-C",
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
    help="path to unit test output dirs",
    default=Path.cwd(),
    required=True,
)
def vue3_unittest(vue3files, output_dir):
    """generating Vue3 unit test"""
    source_code = ""
    for vue3file in vue3files:
        source_code += concatenate_source_files(vue3file)

    final_prompt = VUE_UNITTEST_PROMPT.format(source_code=source_code)
    generated_code = ""

    if os.environ.get("DEBUG") and os.environ.get("DEBUG").lower() == "true":
        print(f"PROMPT:\n {final_prompt}")

    for text in llmclient.invoke_model_generator(final_prompt):
        print(text, end="")
        generated_code += text

    print()
    extract_markdown_code_blocks(generated_code, output_dir)
