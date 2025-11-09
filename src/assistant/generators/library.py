import os

from ..utils.cli.utils import install_requirements
from .base import CodeGenerator


class LibraryProjectInitGenerator(CodeGenerator):

    def generate_pypi_project(self):
        self.generate_library_project("libs/artifactory_pypi_workflow.yml.j2")

    def generate_npm_project(self):
        self.generate_library_project("libs/artifactory_npm_workflow.yml.j2")

    def add_pypi_workflow(self):
        project_root = self.output_dir
        cicd_path = os.path.join(
            project_root, ".github/workflows"
        )  # New tests directory
        # Create backend directories
        self._create_directory(cicd_path)
        self._render_template(
            "libs/artifactory_pypi_workflow.yml.j2",
            os.path.join(cicd_path, "artifactory_pypi_workflow.yml"),
        )

    def add_npm_workflow(self):
        project_root = self.output_dir
        cicd_path = os.path.join(
            project_root, ".github/workflows"
        )  # New tests directory
        # Create backend directories
        self._create_directory(cicd_path)
        self._render_template(
            "libs/artifactory_npm_workflow.yml.j2",
            os.path.join(cicd_path, "artifactory_npm_workflow.yml"),
        )

    def add_docker_workflow(self):
        project_root = self.output_dir
        cicd_path = os.path.join(
            project_root, ".github/workflows"
        )  # New tests directory
        # Create backend directories
        self._create_directory(cicd_path)
        self._render_simple_template(
            "libs/artifactory_docker_workflow.yml.j2",
            os.path.join(cicd_path, "artifactory_docker_workflow.yml"),
        )

    def generate_library_project(self, workflow_jml):
        project_root = self.output_dir
        self._create_directory(project_root)

        src_path = os.path.join(project_root, "src")
        tests_path = os.path.join(project_root, "tests")  # New tests directory
        cicd_path = os.path.join(
            project_root, ".github/workflows"
        )  # New tests directory
        # Create backend directories
        self._create_directory(src_path)
        self._create_directory(tests_path)
        self._create_directory(cicd_path)

        self._render_template(
            "libs/requirements.txt.j2",
            os.path.join(project_root, "requirements.txt"),
        )

        self._render_template(
            "libs/pyproject.toml.j2",
            os.path.join(project_root, "pyproject.toml"),
        )

        self._render_template(
            workflow_jml,
            os.path.join(cicd_path, "artifactory_workflow.yml"),
        )
