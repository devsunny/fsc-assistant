import os
import pathlib
import re

from ..core import templates as template_utils
from ..core.templates import Jinja2TemplateRender


class CodeGenerator:

    def __init__(self, output_dir=".", project_name: str = "Atlas web App"):
        """
        Initializes the project generator.

        Args:
            output_dir (str): The base directory where the project will be created.
                              Defaults to the current directory.
        """
        self.output_dir = os.path.abspath(output_dir)
        self.project_name = project_name
        self.template_render = Jinja2TemplateRender()

    def _create_directory(self, path):
        """
        Helper method to create a directory if it doesn't exist.

        Args:
            path (str): The path of the directory to create.
        """
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")

    def _create_file(self, path, content=""):
        """
        Helper method to create a file with specified content.

        Args:
            path (str): The path of the file to create.
            content (str): The content to write to the file.
        """
        with open(path, "wt", encoding="utf-8") as f:
            f.write(content)
        print(f"Created file: {path}")

    def _render_template(
        self, template_path: str, output_path: str, overwrite=True, **kwarg_context
    ) -> None:
        context = {**kwarg_context}
        project_name = self.project_name.replace("_", " ").replace("-", " ")
        project_name = re.sub(r"[ ]+", " ", project_name)
        context["project_name"] = project_name.lower().capitalize()
        context["project_name_snakecase"] = project_name.replace(" ", "-")
        context["kebab_case_project_name"] = project_name.lower().replace(" ", "-")
        context["capital_project_name"] = project_name.lower().capitalize()
        context["utils"] = template_utils

        self.template_render.render_template(
            template_path, context, output_path, overwrite
        )

    def _render_simple_template(
        self, template_path: str, output_path: str, overwrite=True, **kwarg_context
    ) -> None:
        context = {**kwarg_context}
        project_name = self.project_name.replace("_", " ").replace("-", " ")
        project_name = re.sub(r"[ ]+", " ", project_name)
        context["project_name"] = project_name.lower().capitalize()
        context["project_name_snakecase"] = project_name.replace(" ", "-")
        context["kebab_case_project_name"] = project_name.lower().replace(" ", "-")
        context["capital_project_name"] = project_name.lower().capitalize()
        context["utils"] = template_utils
        tpl_path = pathlib.Path(__file__).parent / "templates" / template_path
        template = pathlib.Path(tpl_path).read_text()
        output = template.replace("PROJECT_NAME", context["project_name"])
        output = output.replace(
            "PROJECT_NAME_SNAKECASE", context["project_name_snakecase"]
        )
        output = output.replace(
            "KEBAB_CASE_PROJECT_NAME", context["kebab_case_project_name"]
        )
        output = output.replace("CAPITAL_PROJECT_NAME", context["capital_project_name"])
        pathlib.Path(output_path).write_text(output)
        print(f"github action CICD workflow created: {output_path}")
