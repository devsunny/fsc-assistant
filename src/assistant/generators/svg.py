import json
import os
from io import StringIO
from typing import Dict, List, Optional

from ..core import templates as utils
from ..llm.client import LLMClient

SVG_PROMPT = """Act as a specialized SVG code generation tool. Your sole purpose is to create valid, well-structured, and minimalist SVG code based on the user's request. Follow these guidelines:
1. Output ONLY valid SVG code without any explanations, comments, or markdown formatting
2. Use scalable vector graphics with appropriate viewBox dimensions
3. Ensure accessibility by including:
   - A title tag with description
   - ARIA labels where applicable
4. Use semantic elements (e.g., <rect>, <circle>, <path>) when possible
5. Maintain proper aspect ratio and responsive design
6. Optimize for web display with minimal code complexity
7. Ensure all text is properly XML-encoded

User Request: 
"{user_input}"
"""


class SVGGenerator:
    def __init__(self, file_path: dir = None):
        self.file_path = file_path

    def generate_text(
        self, file_path, prompt_prefix="", prompt_suffix="", output: str = None
    ):
        prompt_text = ""
        if file_path and os.path.exists(file_path):
            with open(file_path, "rt", encoding="utf-8") as fin:
                prompt_text = fin.read()

        # print(prompt_text)
        review_result = ""
        final_prompt = (
            prompt_prefix
            + "\n"
            + SVG_PROMPT.format(user_input=prompt_text)
            + "\n"
            + prompt_suffix
        )
        llm = LLMClient()

        for text in llm.invoke_model_generator(final_prompt):
            print(text, end="")
            review_result += text

        print("\n")

        basename = os.path.basename(file_path)
        file_name = os.path.splitext(basename)[0]

        final_path = f"{file_name}.svg" if not output else output
        with open(final_path, "wt", encoding="utf-8") as fout:
            fout.write(review_result)
        print(f"pytest is written to {final_path}")
