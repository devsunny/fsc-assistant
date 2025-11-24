"""External service integrations for agents."""

from .github import (
    create_github_pull_request,
    close_github_pull_request,
    list_github_pull_requests,
)
from .jira import (
    add_jira_comment,
    create_jira_issue,
    get_jira_issue,
    update_jira_issue_status,
)


# For backward compatibility, create class-like namespaces
class JiraAgent:
    """JIRA integration functions."""

    get_issue = staticmethod(get_jira_issue)
    update_status = staticmethod(update_jira_issue_status)
    add_comment = staticmethod(add_jira_comment)
    create_issue = staticmethod(create_jira_issue)


class GithubAgent:
    """GitHub integration functions."""

    create_pull_request = staticmethod(create_github_pull_request)
    close_pull_request = staticmethod(close_github_pull_request)
    list_pull_requests = staticmethod(list_github_pull_requests)


__all__ = [
    "JiraAgent",
    "GithubAgent",
    "get_jira_issue",
    "update_jira_issue_status",
    "add_jira_comment",
    "create_jira_issue",
    "create_github_pull_request",
    "close_github_pull_request",
    "list_github_pull_requests",
]