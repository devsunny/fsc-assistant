import json
import os
from io import StringIO
from typing import Dict, List, Optional

from ..core import templates as utils
from ..llm.client import llmclient
from ..prompts.rust import SPECT_TO_RUST_PROMPT


class RustCodeGenerator:
    def __init__(self):
        pass

    def spec_to_rust(self, file_path):
        with open(file_path, "rt", encoding="utf-8") as fin:
            spec = fin.read()

        final_prompt = SPECT_TO_RUST_PROMPT.format(spec=spec)
        generated_code = ""

        with open(file_path + ".code.txt", "wt", encoding="utf-8") as src:
            for text in llmclient.invoke_model_generator(final_prompt):
                print(text, end="")
                src.write(text)
                generated_code += text
