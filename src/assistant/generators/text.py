import json
import os
from io import StringIO
from typing import Dict, List, Optional

from ..core import templates as utils
from ..llm.client import llmclient


class TextGenerator:
    def __init__(self, file_path: dir = None):
        self.file_path = file_path

    def get_next_sequence_file_name(self, file_path):
        outfile = file_path
        basename, ext = os.path.splitext(file_path)
        for idx in range(1000):
            if not os.path.exists(outfile):
                return outfile
            else:
                outfile = f"{basename}_{idx:03d}{ext}"
        return outfile

    def generate_text(self, file_path, output=None):
        with open(file_path, "rt", encoding="utf-8") as fin:
            prompt_text = fin.read()

        review_result = ""
        for text in llmclient.invoke_model_generator(prompt_text):
            print(text, end="")
            review_result += text

        final_path = f"{file_path}.generated.md" if output is None else output
        final_path = self.get_next_sequence_file_name(final_path)
        with open(final_path, "wt", encoding="utf-8") as fout:
            fout.write(review_result)
        print(f"pytest is written to {final_path}")
