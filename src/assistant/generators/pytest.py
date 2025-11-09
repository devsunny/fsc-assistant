import json
import os
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional

from ..agents.utils.markdown import extract_markdown_code_blocks
from ..core import templates as utils
from ..llm.client import LLMClient
from ..utils.cli.utils import get_project_tests_dir
from ..utils.source_code import concatenate_source_files


class PytestGenerator:
    def __init__(self, file_path: Path = None):
        self.file_path = file_path

    def generate_pytest(self):
        files = []
        if os.path.isdir(self.file_path):
            for root, _, files in os.walk(self.file_path):
                for file in files:
                    if file.endswith(".py"):
                        files.append(os.path.join(root, file))
        else:
            files.append(self.file_path)

        for file in files:
            self._generate_test(file)

    def _extract_module_name(
        self, file_path: str, base_dirs: str = ["src", "backend"]
    ) -> str:
        """
        Extracts the fully qualified module name from a Python source file path.

        The function assumes the module's root is a specified base directory.
        It removes the file extension and replaces directory separators with dots.

        Args:
            file_path (str): The absolute or relative path to the source file.
                            Example: 'project_name/src/atlas/dbclient_dremio_flightclient.py'
            base_dir (str, optional): The name of the base directory that marks the
                                    start of the module path. Defaults to "src".

        Returns:
            str: The fully qualified module name.
                Example: 'atlas.dbclient_dremio_flightclient'

        Raises:
            ValueError: If the base directory is not found in the file path.
        """
        # Normalize the path to handle different OS separators
        normalized_path = os.path.normpath(file_path)

        # Split the path into parts
        path_parts = normalized_path.split(os.sep)

        # Find the index of the base directory
        base_index = 0
        try:
            for base_dir in base_dirs:
                if base_dir in path_parts:
                    base_index = path_parts.index(base_dir)
        except ValueError:
            raise ValueError(f"Base directory '{base_dir}' not found in the file path.")

        # Get the subpath from the base directory onwards
        module_subpath_parts = path_parts[base_index + 1 :]

        # Join the subpath parts with a dot and remove the file extension
        module_name = ".".join(
            os.path.splitext(part)[0] for part in module_subpath_parts
        )

        # Handle the case of __init__.py files
        if module_name.endswith(".__init__"):
            module_name = module_name[:-9]  # Remove the .__init__ part

        return module_name

    def generate_pytest_unittest(
        self, file_path: Path, prompt: str, output_dir: Path = None
    ):
        source_content = concatenate_source_files(file_path)

        module_name = self._extract_module_name(file_path)

        final_prompt = prompt.format(
            python_code=source_content, module_name=module_name
        )

        review_result = ""
        llm = LLMClient()
        for text in llm.invoke_model_generator(final_prompt):
            print(text, end="")
            review_result += text

        tests_dir = get_project_tests_dir(file_path, output_dir)

        output_files = extract_markdown_code_blocks(
            review_result, tests_dir, is_test=True
        )
        for file in output_files:
            print(f"pytest unit test file saved to:{file}")

    def _generate_test(self, file_path):
        prompt = """you are tasked to create pytest unit test for the following python code with:
        1. unit test should have at least 95% code coverage
        2. use pytest-mock if necessary
        3. testing target module {module_name}
        4. if testing target extends SecureResource, PublicResource or Resource, it is flask-restx resource, it should be tested with Restful methos
        5. output should only contains python code, no commentary, notes or explanation
        
        ```python
        # {module_name}
        {python_code}        
        ```        
        """
        self.generate_pytest_unittest(file_path, prompt)
