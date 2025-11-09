import json
import os
import re
from io import StringIO
from typing import Dict, List, Optional

from ..core import templates as utils
from ..llm.client import llmclient


class AnyCodeGenerator:
    def __init__(self):
        pass

    def _write_code_file(self, filename, code_buf):
        dir_name = os.path.dirname(filename)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(filename, "wt", encoding="utf-8") as fout:
            fout.write("".join(code_buf))

        print(f"code is written to {filename}")

    def _generate_code(self, prompt):

        final_prompt = f"""You are a code generation assistant. Your task is to write complete, well-commented, and functional code in the specified programming language.

Your output must follow these rules:

Filename Requirement: If the user does not provide a specific filename in their prompt, you must generate a logical filename based on the programming language and the code's purpose.

Output Format: before every generated code block should include path to filename for example (### Filename: cmd/server/main.go)

Prompt: 
{prompt}
  
OUTPUT RULES:
1. Do not include commentary, notes, or explanation in the output


output example:

### Filename: examples/suggested_file_name.json
```json
{{
    "object":{{
        "attr1":12,
        "attr2":"Test"
    }},
    "test_value" : 345.567
}}
```    
### Filename: src/cpu_calculator.copy
```python

class CpuCalculator:
    def __init__(self, *args):
        self.args =args
    
    def do_something(self):
        '''doing some funny thing here'''
    
    def do_more_things(self):
        '''doing more funny thing here'''
```        
"""

        generated_code = ""
        for text in llmclient.invoke_model_generator(final_prompt):
            print(text, end="")
            generated_code += text

        lines = StringIO(generated_code)
        filename = None
        in_code_block = False
        code_buffer = []
        nested_code_block = 0
        for line in lines:
            file_name_match = re.search(r"^[#]{3} Filename: ([a-zA-Z0-9._/]+)$", line)
            code_block_begin = re.search(r"^[`]{3}[a-zA-Z][a-zA-Z0-9]+$", line)
            code_block_end = re.search(r"^[`]{3}$", line)
            if (
                filename is None
                and in_code_block is False
                and file_name_match is not None
            ):
                filename = file_name_match.group(1)
            elif (
                filename is not None
                and in_code_block is False
                and code_block_begin is not None
            ):
                in_code_block = True
            elif (
                filename is not None
                and in_code_block is True
                and code_block_begin is not None
            ):
                nested_code_block += 1
                code_buffer.append(line)
            elif (
                filename is not None
                and in_code_block is True
                and code_block_end is not None
                and nested_code_block > 0
            ):
                nested_code_block -= 1
                code_buffer.append(line)
            elif (
                filename is not None
                and in_code_block is True
                and code_block_end is not None
                and nested_code_block == 0
            ):
                self._write_code_file(filename, code_buffer)
                filename = None
                in_code_block = False
                code_buffer = []
            elif filename is not None and in_code_block is True:
                code_buffer.append(line)
