"""Tests for project-related agent tools."""
from __future__ import annotations

from pathlib import Path

import assistant.agents.tools.project as project


def test_get_current_project_root_folder(monkeypatch, tmp_path, capsys):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    nested_dir = repo_root / "nested"
    nested_dir.mkdir()

    def fake_get_project_root(path: Path | None = None):
        assert path == nested_dir
        return repo_root

    monkeypatch.setattr(project, "get_project_root", fake_get_project_root)
    monkeypatch.chdir(nested_dir)

    result = project.get_current_project_root_folder()
    captured = capsys.readouterr()

    assert result == str(repo_root)
    assert "Current project root folder:" in captured.out


def test_list_files_in_current_project(monkeypatch, tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "file1.txt").write_text("hello")
    data_dir = repo_root / "data"
    data_dir.mkdir()
    (data_dir / "file2.txt").write_text("world")
    (repo_root / ".hidden.txt").write_text("secret")

    monkeypatch.setattr(project, "get_project_root", lambda: repo_root)

    listing = project.list_files_in_current_project()
    entries = set(filter(None, listing.splitlines()))

    assert entries == {"file1.txt", "data/file2.txt"}