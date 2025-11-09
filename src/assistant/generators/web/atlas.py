import os

from assistant.utils.cli.utils import install_requirements

from ..base import CodeGenerator


class AtlasWebProjectInitGenerator(CodeGenerator):

    def _generate_flask_backend_files(self, base_path):
        """
        Generates backend (Flask) specific files and directories.

        Args:
            base_path (str): The base path for the backend directory.
        """
        backend_app_path = os.path.join(base_path, "app")
        backend_api_path = os.path.join(backend_app_path, "api")
        backend_dao_path = os.path.join(backend_app_path, "dao")
        backend_schemas_path = os.path.join(backend_app_path, "schemas")
        backend_models_path = os.path.join(backend_app_path, "models")
        backend_utils_path = os.path.join(backend_app_path, "utils")
        backend_tests_path = os.path.join(base_path, "tests")  # New tests directory

        # Create backend directories
        self._create_directory(backend_dao_path)
        self._create_directory(backend_api_path)
        self._create_directory(backend_app_path)
        self._create_directory(backend_schemas_path)
        self._create_directory(backend_models_path)
        self._create_directory(backend_utils_path)
        self._create_directory(backend_tests_path)  # Create tests directory

        self._create_file(os.path.join(backend_app_path, "__init__.py"))
        self._create_file(os.path.join(backend_api_path, "__init__.py"))
        self._create_file(os.path.join(backend_dao_path, "__init__.py"))
        self._create_file(os.path.join(backend_schemas_path, "__init__.py"))
        self._create_file(os.path.join(backend_models_path, "__init__.py"))
        self._create_file(os.path.join(backend_utils_path, "__init__.py"))
        self._create_file(os.path.join(backend_tests_path, "__init__.py"))

        self._render_template(
            "atlas_web/main.py.j2", os.path.join(backend_app_path, "main.py")
        )
        self._render_template(
            "atlas_web/app_session.py.j2",
            os.path.join(backend_app_path, "app_session.py"),
        )
        self._render_template(
            "atlas_web/routes.py.j2",
            os.path.join(backend_app_path, "routes.py"),
        )
        self._render_template(
            "atlas_web/requirements.txt.j2",
            os.path.join(base_path, "requirements.txt"),
        )

        self._render_template(
            "atlas_web/pytest.py.j2",
            os.path.join(base_path, "pytest.ini"),
        )
        install_requirements(os.path.join(base_path, "requirements.txt"))

    def generate_flask_backend_project(self):
        project_root = self.output_dir
        self._create_directory(project_root)
        backend_path = os.path.join(project_root, "backend")
        self._create_directory(backend_path)
        print(f"Generating backend project in: {backend_path}")
        self._generate_flask_backend_files(backend_path)
