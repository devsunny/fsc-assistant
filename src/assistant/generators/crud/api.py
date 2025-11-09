import os
import re
from typing import Dict, List, Optional

from pgsql_parser import Column, ForeignKey, Table  # Added as requested, commented out

from assistant.utils.cli.utils import load_atlas_env, match_database_type

from ...core import templates as utils
from ...core.templates import Jinja2TemplateRender
from ..api.base import APIGenerator


class CRUDApiGenerator(APIGenerator):

    def generate_crud(self, tables: List[Table]):
        print(f"number of input tables:{len(tables)}")
        all_tables = tables
        for tb in all_tables:
            print(f"generating CRUD artifact for {tb.name}-- {tb.table_type}")
            self.render_model(tb)
            self.render_schema(tb)
            self.render_api(tb)
            self.render_dao(tb)
            print(f"table {tb}'s CRUD artifact were created")
        self.render_router(all_tables)

    def render_api(self, table: Table):
        output_path = os.path.join(self.project_root_dir, self.backend_dir, "app/api")
        self.render_template(table, "backend/api_resources.py.j2", output_path)

    def render_schema(self, table: Table):
        output_path = os.path.join(
            self.project_root_dir, self.backend_dir, "app/schemas"
        )
        self.render_template(table, "backend/schema.py.j2", output_path)

    def render_model(self, table: Table):
        output_path = os.path.join(
            self.project_root_dir, self.backend_dir, "app/models"
        )
        self.render_template(table, "backend/model.py.j2", output_path)

    def render_dao(self, table: Table):
        output_path = os.path.join(self.project_root_dir, self.backend_dir, "app/dao")
        self.render_template(table, "backend/dao.py.j2", output_path)

    def render_router(self, tables: List[Table]):
        router_path = os.path.join(
            self.project_root_dir, self.backend_dir, "app/router.py"
        )
        import_lines = []
        def_funct = None
        api_lines = []
        if os.path.exists(router_path):
            with open(router_path, "rt", encoding="utf-8") as fin:
                for line in fin:
                    code = line.strip()
                    if code.startswith("from "):
                        import_lines.append(code)
                    elif code.startswith("def "):
                        def_funct = code
                    elif code.startswith("api."):
                        api_lines.append(code)

        for table in tables:
            import_line = f"from .api.{utils.to_singular_snake_case(table.name)} import ns_{utils.to_plural_snake_case(table.name)}"
            api_line = f"api.add_namespace(ns_{utils.to_plural_snake_case(table.name)})"
            if import_line not in import_lines:
                import_lines.append(import_line)
            if api_line not in api_lines:
                api_lines.append(api_line)

        if not api_lines:
            api_lines.append("pass")

        def_funct = def_funct or "def init_route(api):"
        with open(router_path, "wt", encoding="utf-8") as fout:
            fout.write("\n".join(import_lines))
            fout.write("\n\n\n")
            fout.write(def_funct)
            fout.write("\n")
            api_lines = [f"    {code}" for code in api_lines]
            fout.write("\n".join(api_lines))
            fout.write("\n")
