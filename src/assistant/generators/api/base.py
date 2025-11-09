import os
import re
from typing import Dict, List, Optional

from pgsql_parser import ForeignKey, Table  # Added as requested, commented out

from assistant.utils.cli.utils import load_atlas_env, match_database_type

from ...core import templates as utils
from ...core.faker import DataGenerator
from ..base import CodeGenerator


class APIGenerator(CodeGenerator):
    def __init__(self, tables: Optional[List[Table]] = None):
        self.phanes_cfg = load_atlas_env()
        self.project_root_dir = self.phanes_cfg["project_root_dir"]
        self.project_name = self.phanes_cfg["project_name"]
        super().__init__(self.project_root_dir, self.project_name)
        self.tables = tables
        self.backend_dir = self.phanes_cfg["backend"]["dir"]
        self.database_type = self.phanes_cfg["database"]["type"]
        self.fake_data = None
        self.another_fake_data = None
        self.third_fake_data = None

    def render_query_template(
        self,
        query: str,
        table: Table,
        template_path: str,
        output_dir: str,
        pytest: bool = False,
    ) -> Dict:
        name = table.name
        table_singular_snakecase_name = utils.to_singular_snake_case(name)
        table_plural_snakecase_name = utils.to_plural_snake_case(name)
        table_singular_pascal_name = utils.to_singular_pascal_case(name)
        table_plural_pascal_name = utils.to_plural_pascal_case(name)
        table_kebab_case_name = table_plural_snakecase_name.replace("_", "-")
        is_postgres = match_database_type("postgresql")
        context = {
            "table": table,
            "query": query,
            "columns": table.columns.values(),
            "table_singular_snakecase_name": table_singular_snakecase_name,
            "table_singular_pascal_name": table_singular_pascal_name,
            "table_plural_snakecase_name": table_plural_snakecase_name,
            "table_plural_pascal_name": table_plural_pascal_name,
            "table_kebab_case_name": table_kebab_case_name,
            "is_postgres": is_postgres,
            "db_type": self.database_type,
            "utils": utils,
        }
        project_name = self.project_name.replace("_", " ").replace("-", " ")
        project_name = re.sub(r"[ ]+", " ", project_name)
        context["project_name"] = project_name.lower().capitalize()
        context["kebab_case_project_name"] = project_name.lower().replace(" ", "-")
        context["capital_project_name"] = project_name.lower().capitalize()

        out_file_name = (
            f"test_{table_singular_snakecase_name}.py"
            if pytest is True
            else f"{table_singular_snakecase_name}.py"
        )
        output_path = os.path.join(output_dir, out_file_name)
        print("create file:", output_path)
        self.template_render.render_template(template_path, context, output_path, True)

    def render_template(
        self, table: Table, template_path: str, output_dir: str, pytest: bool = False
    ) -> Dict:

        if pytest is True:
            fake_data = DataGenerator(table).generate_fake_data(3)
            self.fake_data = fake_data[0]
            self.another_fake_data = fake_data[1]
            self.third_fake_data = fake_data[2]

        table_singular_snakecase_name = utils.to_singular_snake_case(table.name)
        table_plural_snakecase_name = utils.to_plural_snake_case(table.name)
        table_singular_pascal_name = utils.to_singular_pascal_case(table.name)
        table_plural_pascal_name = utils.to_plural_pascal_case(table.name)
        table_kebab_case_name = table_plural_snakecase_name.replace("_", "-")

        is_postgres = match_database_type("postgresql")

        composite_fks: List[ForeignKey] = (
            [fk for fk in table.foreign_keys if len(fk.columns) > 1]
            if table.foreign_keys
            else []
        )
        has_table_args: bool = len(composite_fks) > 0 or (
            table.schema is not None and len(table.schema) > 1
        )
        child_relationships = utils.get_child_relationships(table, self.tables)
        context = {
            "table": table,
            "columns": table.columns.values(),
            "composite_fks": composite_fks,
            "pk_columns": utils.get_pk_columns(table),
            "non_pk_columns": utils.get_non_pk_columns(table),
            "has_table_args": has_table_args,
            "table_singular_snakecase_name": table_singular_snakecase_name,
            "table_singular_pascal_name": table_singular_pascal_name,
            "table_plural_snakecase_name": table_plural_snakecase_name,
            "table_plural_pascal_name": table_plural_pascal_name,
            "table_kebab_case_name": table_kebab_case_name,
            "is_postgres": is_postgres,
            "child_relationships": child_relationships,
            "db_type": self.database_type,
            "utils": utils,
            "fake_data": self.fake_data,
            "another_fake_data": self.another_fake_data,
            "third_fake_data": self.third_fake_data,
        }
        project_name = self.project_name.replace("_", " ").replace("-", " ")
        project_name = re.sub(r"[ ]+", " ", project_name)
        context["project_name"] = project_name.lower().capitalize()
        context["kebab_case_project_name"] = project_name.lower().replace(" ", "-")
        context["capital_project_name"] = project_name.lower().capitalize()

        out_file_name = (
            f"test_{table_singular_snakecase_name}.py"
            if pytest is True
            else f"{table_singular_snakecase_name}.py"
        )
        output_path = os.path.join(output_dir, out_file_name)
        print("create file:", output_path)
        self.template_render.render_template(template_path, context, output_path, True)
