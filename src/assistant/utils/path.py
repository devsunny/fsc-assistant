import os
from pathlib import Path
from typing import List, Union


def get_project_root(file_path: Union[Path, str] = None, max_depths: int = 50) -> Path:
    if file_path is None:
        file_path = Path.cwd()
    file_path = Path(file_path) if isinstance(file_path, str) else file_path
    depth = 0
    while depth < max_depths:
        if file_path.is_file():
            file_path = file_path.parent

        git_dir = file_path / ".git"
        if git_dir.exists() and git_dir.is_dir():
            return file_path.resolve()

        github_dir = file_path / ".github"
        if github_dir.exists() and github_dir.is_dir():
            return file_path.resolve()

        vscode_dir = file_path / ".vscode"
        if vscode_dir.exists() and vscode_dir.is_dir():
            return file_path.resolve()

        tgt_dir = file_path / "specs"
        if tgt_dir.exists() and tgt_dir.is_dir():
            return file_path.resolve()

        tgt_dir = file_path / "openspec"
        if tgt_dir.exists() and tgt_dir.is_dir():
            return file_path.resolve()

        depth += 1
        file_path = file_path.parent
    return Path.cwd().resolve()


def get_project_spec_dirs(project_root_path: Union[Path, str]) -> List[Path]:
    project_root_path = (
        Path(project_root_path)
        if isinstance(project_root_path, str)
        else project_root_path
    )
    search_paths = []
    openspec_path = project_root_path / "openspec/specs"
    if openspec_path.exists() and openspec_path.is_dir():
        search_paths.append(openspec_path)
    custom_specs_path = project_root_path / "specs"
    if custom_specs_path.exists() and custom_specs_path.is_dir():
        search_paths.append(custom_specs_path)
    if not search_paths:
        search_paths.append(Path.cwd().resolve())

    return search_paths


def find_spec_file(
    project_root_path: Union[Path, str], spec_filename: str
) -> List[Path]:
    project_root_path = (
        Path(project_root_path)
        if isinstance(project_root_path, str)
        else project_root_path
    )
    spec_file = project_root_path / spec_filename
    if spec_file.exists() and spec_file.is_file():
        return spec_file
    search_paths = get_project_spec_dirs(project_root_path)
    for search_path in search_paths:
        spec_file = search_path / spec_filename
        if spec_file.exists() and spec_file.is_file():
            return spec_file
    spec_filename = os.path.basename(spec_filename)
    for search_path in search_paths:
        spec_file = search_path / spec_filename
        if spec_file.exists() and spec_file.is_file():
            return spec_file

    raise FileNotFoundError(f"not able to find spec file: {spec_filename}")


def find_spec_folder(project_root_path: Union[Path, str]) -> Path:
    openspec_path = project_root_path / "openspec/specs"
    if openspec_path.exists() and openspec_path.is_dir():
        return openspec_path
    custom_specs_path = project_root_path / "specs"
    if not custom_specs_path.exists():
        custom_specs_path.mkdir(exist_ok=True)
    return custom_specs_path


def get_relative_path(root_path: Union[Path, str], file_path: Union[Path, str]):
    root_path = Path(root_path) if isinstance(root_path, str) else root_path
    file_path = Path(file_path) if isinstance(file_path, str) else file_path
    rel_path = os.path.relpath(file_path, start=root_path)
    return Path(rel_path)
