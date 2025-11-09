# tools.py

from ..integrations.github import create_github_pull_request
from ..integrations.jira import (
    add_jira_comment,
    create_jira_issue,
    get_jira_issue,
    update_jira_issue_status,
)
from .builtin import (
    get_current_local_time,
    get_current_project_folder,
    load_image_files,
    load_text_file_from_disk,
    run_shell_command,
    save_text_file_to_disk,
)

# from .document import (
#     convert_document_to_markdown,
#     extract_all_tables_from_document_to_markdown,
#     extract_table_from_document_to_markdown,
# )
from .repository import InMemoryToolsRepository
from .web import read_web_page, capture_web_page_screenshot, search_google


CORE_TOOLS = [
    run_shell_command,
    get_current_local_time,
    load_image_files,
    save_text_file_to_disk,
    load_text_file_from_disk,
    get_current_project_folder,
]

# EXTRACTION_TOOLS = [
#     extract_table_from_document_to_markdown,
#     extract_all_tables_from_document_to_markdown
# ]

# DOCUMENT_ANALYSIS_TOOLS = [
#     convert_document_to_markdown,
# ]

WEB_TOOLS = [
    read_web_page,
    capture_web_page_screenshot,
    search_google,
]


JIRA_TOOLS = [
    get_jira_issue,
    update_jira_issue_status,
    add_jira_comment,
    create_jira_issue,
]

GITHUB_TOOLS = [create_github_pull_request]

# Keep for backward compatibility
tools = CORE_TOOLS + WEB_TOOLS + JIRA_TOOLS + GITHUB_TOOLS


def create_default_repository() -> InMemoryToolsRepository:
    """
    Create and populate a default tools repository.

    Registers all builtin tools, integration tools (LiteLLM, JIRA, GitHub),
    web tools, and special category tools (extraction, document_analysis).

    Returns:
        InMemoryToolsRepository with all default tools registered
    """
    repository = InMemoryToolsRepository()
    # Register builtin tools
    # repository.register_tools(CORE_TOOLS, category="builtin")
    # Register web tools
    repository.register_tools(WEB_TOOLS, category="web")
    # Register integration tools
    repository.register_tools(LITE_LLM_TOOLS, category="integration")
    repository.register_tools(JIRA_TOOLS, category="integration")
    repository.register_tools(GITHUB_TOOLS, category="integration")
    # Register special category tools
    # repository.register_tools(EXTRACTION_TOOLS, category="extraction")
    # repository.register_tools(DOCUMENT_ANALYSIS_TOOLS, category="document_analysis")

    return repository
