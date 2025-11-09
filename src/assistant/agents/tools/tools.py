# tools.py
from ..integrations.github import create_github_pull_request
from ..integrations.jira import (
    add_jira_comment,
    create_jira_issue,
    get_jira_issue,
    update_jira_issue_status,
)
from .core_tools import (
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

from .web import read_web_page, capture_web_page_screenshot, search_google


CORE_TOOLS = [
    run_shell_command,
    get_current_local_time,
    load_image_files,
    save_text_file_to_disk,
    load_text_file_from_disk,
    get_current_project_folder,
]


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
