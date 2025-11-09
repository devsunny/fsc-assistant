import json
import os
from io import StringIO
from typing import Dict, List, Optional

from ..agents.utils.markdown import extract_markdown_code_blocks
from ..core import templates as utils
from ..llm.client import llmclient
from ..prompts.python import ADHOC_PROMPT, CUCUMBER_BBD_PROMPT, SPEC_PROMPT


class PythonCodeGenerator:
    def __init__(self):
        pass

    def _generate_python(self, final_prompt):
        generated_code = ""
        for text in llmclient.invoke_model_generator(final_prompt):
            print(text, end="")
            generated_code += text

        lines = StringIO(generated_code)
        codes = [line for line in lines if not line.startswith("```")]
        file_name = codes[0][1:].strip()
        code_lines = codes[1:]

        with open(file_name, "wt", encoding="utf-8") as fout:
            fout.write("".join(codes))
            # end overwrite file
        print(f"python code is written to {file_name}")

    def generate_python(self, prompt):

        final_prompt = ADHOC_PROMPT.format(prompt=prompt)
        self._generate_python(final_prompt)

    def bdd_to_python(self, file_path):
        with open(file_path, "rt", encoding="utf-8") as fin:
            cucumber_bdd_spec = fin.read()

        final_prompt = CUCUMBER_BBD_PROMPT.format(cucumber_bdd_spec=cucumber_bdd_spec)
        generated_code = ""
        for text in llmclient.invoke_model_generator(final_prompt):
            print(text, end="")
            generated_code += text

        lines = StringIO(generated_code)
        codes = [line for line in lines if not line.startswith("```")]
        file_name = codes[0][1:].strip()
        code_lines = codes[1:]

        with open(file_name, "wt", encoding="utf-8") as fout:
            fout.write("".join(codes))
            # end overwrite file
        print(f"python code is written to {file_name}")
        extract_markdown_code_blocks(generated_code, os.getcwd())

    def spec_to_python(self, file_path, model_id: Optional[str] = None):
        print(f"start reading spec: {file_path}")
        try:
            with open(file_path, "rt", encoding="utf-8") as fin:
                spec = fin.read()

            final_prompt = SPEC_PROMPT.format(spec=spec)
            generated_code = ""

            if os.environ.get("DEBUG") and os.environ.get("DEBUG").lower() == "true":
                print(f"PROMPT:\n {final_prompt}")
            with open(file_path + ".spec_code.txt", "wt", encoding="utf-8") as src:
                for text in llmclient.invoke_model_generator(
                    final_prompt, model_id=model_id
                ):
                    print(text, end="")
                    src.write(text)
                    generated_code += text

            print("\n")
            if os.environ.get("DEBUG") and os.environ.get("DEBUG").lower() == "true":
                print(f"PROMPT:\n {final_prompt}")

            extract_markdown_code_blocks(generated_code, os.getcwd())

        except Exception as e:
            import traceback

            traceback.print_exception(e)
