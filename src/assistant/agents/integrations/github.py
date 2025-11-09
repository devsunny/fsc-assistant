"""
GitHub Integration Agent

This module provides GitHub API integration for Kara Code agentic workflows.
It enables creating pull requests programmatically from feature branches.

Functions:
    create_github_pull_request: Create a pull request from a feature branch
"""

import logging
from typing import Any, Dict, Optional

from github import Github, GithubException

from assistant.config.manager import AssistantConfig

logger = logging.getLogger(__name__)


def _get_github_client() -> tuple[Optional[Github], Optional[str]]:
    """
    Create and return a GitHub client instance using configuration.

    Returns:
        tuple: (Github client instance, error message)
               Returns (None, error_msg) if configuration is missing or invalid
    """
    try:
        config = AssistantConfig()
        token = config.get_option("github", "token")

        if not token:
            return None, (
                "GitHub configuration missing. Please configure GitHub token in "
                ".fsc-assistant.env.toml with [github] section containing: token"
            )

        # Create GitHub client with token
        github_client = Github(token)

        # Test authentication by getting the authenticated user
        try:
            github_client.get_user().login
        except GithubException as e:
            if e.status == 401:
                return None, "Authentication failed. Please check your GitHub token."
            raise

        return github_client, None

    except Exception as e:
        logger.error(f"Failed to create GitHub client: {e}")
        return None, f"Failed to create GitHub client: {str(e)}"


def create_github_pull_request(
    repo: str, title: str, body: str, head: str, base: str = "main", draft: bool = False
) -> Dict[str, Any]:
    """
    Create a new GitHub pull request from a feature branch.

    Args:
        repo: Repository specification - "owner/repo" or just "repo" if default_owner is set
        title: Pull request title (required)
        body: Pull request description (required)
        head: Source branch name (required)
        base: Target branch name (default: "main")
        draft: Create as draft PR (default: False)

    Returns:
        dict with keys:
            - success: bool
            - pull_request: dict (if success=True) with fields:
                - number: PR number
                - url: API URL
                - html_url: Web URL
                - title, body, state, draft
                - head: dict with ref and sha
                - base: dict with ref and sha
                - created_at: timestamp
                - user: dict with login
            - error: str (if success=False)
            - error_type: str (if success=False)

    Example:
        >>> result = create_github_pull_request(
        ...     repo="myorg/myrepo",
        ...     title="Fix: Resolve login bug",
        ...     body="This PR fixes the login issue",
        ...     head="feature/fix-login",
        ...     base="main"
        ... )
        >>> if result["success"]:
        ...     print(f"PR created: {result['pull_request']['html_url']}")

        >>> # With default_owner configured
        >>> result = create_github_pull_request(
        ...     repo="myrepo",
        ...     title="WIP: New feature",
        ...     body="Work in progress...",
        ...     head="feature/new-feature",
        ...     draft=True
        ... )
    """
    try:
        # Validate required parameters
        validation_errors = []
        if not repo or not repo.strip():
            validation_errors.append("Repository is required")
        if not title or not title.strip():
            validation_errors.append("Title is required")
        if not body or not body.strip():
            validation_errors.append("Body is required")
        if not head or not head.strip():
            validation_errors.append("Head branch is required")

        if validation_errors:
            return {
                "success": False,
                "error": "; ".join(validation_errors),
                "error_type": "validation_error",
            }

        # Get GitHub client
        github_client, error = _get_github_client()
        if error:
            return {
                "success": False,
                "error": error,
                "error_type": "configuration_error",
            }

        # Parse repository specification
        config = AssistantConfig()
        if "/" in repo:
            # Explicit owner/repo format
            owner, repo_name = repo.split("/", 1)
        else:
            # Use default owner from config
            default_owner = config.get_option("github", "default_owner")
            if not default_owner:
                return {
                    "success": False,
                    "error": (
                        f"Repository '{repo}' is missing owner. Either provide "
                        "'owner/repo' format or configure 'default_owner' in "
                        "[github] section of .fsc-assistant.env.toml"
                    ),
                    "error_type": "validation_error",
                }
            owner = default_owner
            repo_name = repo

        # Get repository object
        try:
            repository = github_client.get_repo(f"{owner}/{repo_name}")
        except GithubException as e:
            logger.error(f"GitHub error accessing repository {owner}/{repo_name}: {e}")

            if e.status == 404:
                return {
                    "success": False,
                    "error": f"Repository not found: {owner}/{repo_name}",
                    "error_type": "repository_not_found",
                }
            elif e.status == 401:
                return {
                    "success": False,
                    "error": "Authentication failed. Please check your GitHub token.",
                    "error_type": "authentication_error",
                }
            elif e.status == 403:
                return {
                    "success": False,
                    "error": f"Permission denied for repository: {owner}/{repo_name}",
                    "error_type": "permission_error",
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub error: {str(e)}",
                    "error_type": "github_error",
                }

        # Validate head branch exists
        try:
            repository.get_branch(head)
        except GithubException as e:
            if e.status == 404:
                return {
                    "success": False,
                    "error": f"Head branch not found: {head}",
                    "error_type": "branch_not_found",
                }
            else:
                return {
                    "success": False,
                    "error": f"Error checking head branch: {str(e)}",
                    "error_type": "github_error",
                }

        # Validate base branch exists
        try:
            repository.get_branch(base)
        except GithubException as e:
            if e.status == 404:
                return {
                    "success": False,
                    "error": f"Base branch not found: {base}",
                    "error_type": "branch_not_found",
                }
            else:
                return {
                    "success": False,
                    "error": f"Error checking base branch: {str(e)}",
                    "error_type": "github_error",
                }

        # Create pull request
        try:
            pr = repository.create_pull(
                title=title, body=body, head=head, base=base, draft=draft
            )

            logger.info(
                f"Successfully created pull request #{pr.number} in {owner}/{repo_name} "
                f"(head: {head}, base: {base}, draft: {draft})"
            )

        except GithubException as e:
            logger.error(f"GitHub error creating pull request: {e}")

            if e.status == 422:
                # Unprocessable entity - could be duplicate PR, no commits, etc.
                error_msg = (
                    str(e.data.get("errors", [{}])[0].get("message", str(e)))
                    if hasattr(e, "data")
                    else str(e)
                )
                return {
                    "success": False,
                    "error": f"Cannot create pull request: {error_msg}",
                    "error_type": "validation_error",
                }
            elif e.status == 403:
                return {
                    "success": False,
                    "error": f"Permission denied to create pull request in {owner}/{repo_name}",
                    "error_type": "permission_error",
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub error: {str(e)}",
                    "error_type": "github_error",
                }

        # Build response with PR details
        pr_data = {
            "number": pr.number,
            "url": pr.url,
            "html_url": pr.html_url,
            "title": pr.title,
            "body": pr.body or "",
            "state": pr.state,
            "draft": pr.draft,
            "head": {"ref": pr.head.ref, "sha": pr.head.sha},
            "base": {"ref": pr.base.ref, "sha": pr.base.sha},
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
            "user": {"login": pr.user.login if pr.user else None},
        }

        return {"success": True, "pull_request": pr_data}

    except Exception as e:
        logger.error(f"Unexpected error creating pull request: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown",
        }
