import os
from typing import Dict, List, Optional

from pgsql_parser import ForeignKey, SQLParser, Table

from ...core import templates as utils
from ...generators.query_name import create_query_name
from .base import APIGenerator


class AtlasWebApiGenerator(APIGenerator):

    def generate_query_service(self, sql_query: str):
        sqlparser = SQLParser(sql_query)
        all_tables = sqlparser.get_tables()
        for table_name in all_tables:
            table = all_tables[table_name]
            service_name = create_query_name(table_name)
            table.name = service_name
            output_path = os.path.join(
                self.project_root_dir, self.backend_dir, "app/dao"
            )
            self.render_query_template(
                table_name, table, "atlas_web/query_dao.py.j2", output_path
            )
            output_path = os.path.join(
                self.project_root_dir, self.backend_dir, "app/schemas"
            )
            self.render_query_template(
                table_name, table, "atlas_web/query_schema.py.j2", output_path
            )
            output_path = os.path.join(
                self.project_root_dir, self.backend_dir, "app/api"
            )
            self.render_query_template(
                table_name, table, "atlas_web/query_api_resources.py.j2", output_path
            )
            self.render_router([table])
        pass

    def generate_crud(self, tables: List[Table]):
        print(f"number of input tables:{len(tables)}")
        all_tables = tables
        for tb in all_tables:
            print(f"generating CRUD artifact for {tb.name}-- {tb.table_type}")
            self.render_model(tb)
            self.render_schema(tb)
            self.render_api(tb)
            self.render_dao(tb)
            self.render_tests(tb)
            print(f"table {tb}'s CRUD artifact were created")
        self.render_router(all_tables)

    def render_api(self, table: Table):
        output_path = os.path.join(self.project_root_dir, self.backend_dir, "app/api")
        self.render_template(table, "atlas_web/api_resources.py.j2", output_path)

    def render_schema(self, table: Table):
        output_path = os.path.join(
            self.project_root_dir, self.backend_dir, "app/schemas"
        )
        self.render_template(table, "atlas_web/schema.py.j2", output_path)

    def render_model(self, table: Table):
        output_path = os.path.join(
            self.project_root_dir, self.backend_dir, "app/models"
        )
        self.render_template(table, "atlas_web/model.py.j2", output_path)

    def render_dao(self, table: Table):
        output_path = os.path.join(self.project_root_dir, self.backend_dir, "app/dao")
        self.render_template(table, "atlas_web/dao.py.j2", output_path)

    def render_tests(self, table: Table):
        output_path = os.path.join(self.project_root_dir, self.backend_dir, "tests")
        self.render_template(table, "atlas_web/pytest.py.j2", output_path, pytest=True)

    def render_router(self, tables: List[Table]):
        router_path = os.path.join(
            self.project_root_dir, self.backend_dir, "app/routes.py"
        )
        import_lines = []
        def_funct = None
        api_lines = []
        module_comment = None
        funct_comment = None
        funct_init_line = "    api = atlaswebapp.rest_api"

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
                    elif code.startswith('"""'):
                        if not module_comment:
                            module_comment = code
                        else:
                            funct_comment = code
                    elif code == "api = atlaswebapp.rest_api":
                        pass

        for table in tables:
            import_line = f"from .api.{utils.to_singular_snake_case(table.name)} import ns_{utils.to_plural_snake_case(table.name)}"
            api_line = f"api.add_namespace(ns_{utils.to_plural_snake_case(table.name)})"
            if import_line not in import_lines:
                import_lines.append(import_line)
            if api_line not in api_lines:
                api_lines.append(api_line)

        if not api_lines:
            api_lines.append("pass")

        def_funct = def_funct or "def initialize_routes(atlaswebapp):"
        with open(router_path, "wt", encoding="utf-8") as fout:
            fout.write("\n".join(import_lines))
            fout.write("\n\n\n")
            fout.write(def_funct)
            fout.write("\n")
            fout.write(funct_init_line)
            fout.write("\n")
            api_lines = [f"    {code}" for code in api_lines]
            fout.write("\n".join(api_lines))
            fout.write("\n")
        pass
