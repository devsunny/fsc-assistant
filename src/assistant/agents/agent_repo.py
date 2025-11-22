"""Tool repository with lazy loading for performance optimization."""

from typing import List, Any

# Lazy loading cache
_core_tools_cache = None
_integration_tools_cache = None
_tools_cache = None


def _load_core_tools() -> List[Any]:
    """Load core tools on first access."""
    global _core_tools_cache
    if _core_tools_cache is None:
        from .tools import (
            run_shell_command,
            get_current_local_time,
            get_current_project_root_folder,
            list_files_in_current_project,
            save_text_file_to_disk,
            load_text_file_from_disk,
            save_binary_file_to_disk,
            load_image_files_from_disk,
            change_working_directory,
        )
        from .web import (
            fetch_webpage_content,
            capture_web_page_screenshot,
            download_web_file_from_url,
            search_google_custom_api,
        )

        _core_tools_cache = [
            run_shell_command,
            get_current_local_time,
            get_current_project_root_folder,
            list_files_in_current_project,
            save_text_file_to_disk,
            load_text_file_from_disk,
            save_binary_file_to_disk,
            load_image_files_from_disk,
            change_working_directory,
            fetch_webpage_content,
            capture_web_page_screenshot,
            download_web_file_from_url,
            search_google_custom_api,
        ]
    return _core_tools_cache


def _load_integration_tools() -> List[Any]:
    """Load integration tools on first access."""
    global _integration_tools_cache
    if _integration_tools_cache is None:
        from .integrations import (
            get_jira_issue,
            update_jira_issue_status,
            add_jira_comment,
            create_jira_issue,
            create_github_pull_request,
        )

        _integration_tools_cache = [
            get_jira_issue,
            update_jira_issue_status,
            add_jira_comment,
            create_jira_issue,
            create_github_pull_request,
        ]
    return _integration_tools_cache


def load_tools() -> List[Any]:
    """Get all available tools (lazy loaded)."""
    global _tools_cache
    if _tools_cache is None:
        _tools_cache = _load_core_tools() + _load_integration_tools()
    return _tools_cache