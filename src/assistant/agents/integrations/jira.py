"""
JIRA Integration Agent

This module provides JIRA API integration for Kara Code agentic workflows.
It enables querying issue details, updating issue status, adding comments,
and creating new issues in JIRA programmatically.

Functions:
    get_jira_issue: Query and retrieve JIRA issue details
    update_jira_issue_status: Update issue status and optionally reassign
    add_jira_comment: Add comments to JIRA issues
    create_jira_issue: Create new JIRA issues
"""

import logging
from typing import Any, Dict, List, Optional

from jira import JIRA
from jira.exceptions import JIRAError
from assistant.config.manager import AssistantConfig

logger = logging.getLogger(__name__)


def _get_jira_client() -> tuple[Optional[JIRA], Optional[str]]:
    """
    Create and return a JIRA client instance using configuration.

    Returns:
        tuple: (JIRA client instance, error message)
               Returns (None, error_msg) if configuration is missing or invalid
    """
    try:
        config = AssistantConfig()
        base_url = config.get_option("jira", "base_url")
        username = config.get_option("jira", "username")
        api_token = config.get_option("jira", "api_token")

        if not base_url or not username or not api_token:
            return None, (
                "JIRA configuration missing. Please configure JIRA credentials in "
                ".fsc-assistant.env.toml with [jira] section containing: base_url, "
                "username, and api_token"
            )

        # Create JIRA client with basic auth
        jira_client = JIRA(server=base_url, basic_auth=(username, api_token))

        return jira_client, None

    except Exception as e:
        logger.error(f"Failed to create JIRA client: {e}")
        return None, f"Failed to create JIRA client: {str(e)}"


def get_jira_issue(issue_key: str) -> Dict[str, Any]:
    """
    Query and retrieve JIRA issue details.

    Args:
        issue_key: JIRA issue key (e.g., "PROJ-123")

    Returns:
        dict with keys:
            - success: bool
            - issue: dict (if success=True) with fields:
                - key, summary, description, status, assignee,
                  reporter, created, updated, comments
            - error: str (if success=False)
            - error_type: str (if success=False)

    Example:
        >>> result = get_jira_issue("PROJ-123")
        >>> if result["success"]:
        ...     print(f"Issue: {result['issue']['summary']}")
    """
    try:
        jira_client, error = _get_jira_client()
        if error:
            return {
                "success": False,
                "error": error,
                "error_type": "configuration_error",
            }

        # Fetch issue from JIRA
        issue = jira_client.issue(issue_key)

        # Extract assignee information
        assignee_info = None
        if issue.fields.assignee:
            assignee_info = {
                "name": issue.fields.assignee.displayName,
                "email": getattr(issue.fields.assignee, "emailAddress", None),
            }

        # Extract reporter information
        reporter_info = None
        if issue.fields.reporter:
            reporter_info = {
                "name": issue.fields.reporter.displayName,
                "email": getattr(issue.fields.reporter, "emailAddress", None),
            }

        # Extract comments
        comments_list = []
        if hasattr(issue.fields, "comment") and issue.fields.comment:
            for comment in issue.fields.comment.comments:
                comments_list.append(
                    {
                        "id": comment.id,
                        "author": comment.author.displayName,
                        "body": comment.body,
                        "created": comment.created,
                    }
                )

        # Build response
        issue_data = {
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description or "",
            "status": issue.fields.status.name,
            "assignee": assignee_info,
            "reporter": reporter_info,
            "created": issue.fields.created,
            "updated": issue.fields.updated,
            "comments": comments_list,
        }

        logger.info(f"Successfully retrieved JIRA issue: {issue_key}")
        return {"success": True, "issue": issue_data}

    except JIRAError as e:
        logger.error(f"JIRA error retrieving issue {issue_key}: {e}")

        # Handle specific JIRA errors
        if e.status_code == 404:
            return {
                "success": False,
                "error": f"Issue not found: {issue_key}",
                "error_type": "not_found",
            }
        elif e.status_code == 401:
            return {
                "success": False,
                "error": "Authentication failed. Please check your JIRA credentials.",
                "error_type": "authentication_error",
            }
        elif e.status_code == 403:
            return {
                "success": False,
                "error": f"Permission denied for issue: {issue_key}",
                "error_type": "permission_error",
            }
        else:
            return {
                "success": False,
                "error": f"JIRA error: {str(e)}",
                "error_type": "jira_error",
            }

    except Exception as e:
        logger.error(f"Unexpected error retrieving issue {issue_key}: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown",
        }


def update_jira_issue_status(
    issue_key: str, status: str, assignee: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update JIRA issue status and optionally reassign.

    Args:
        issue_key: JIRA issue key (e.g., "PROJ-123")
        status: Target status (e.g., "In Progress", "Done", "QA")
        assignee: Optional username or email to assign issue to

    Returns:
        dict with keys:
            - success: bool
            - issue: dict (if success=True) with updated fields
            - error: str (if success=False)
            - error_type: str (if success=False)

    Example:
        >>> result = update_jira_issue_status("PROJ-123", "In Progress", "qa@example.com")
        >>> if result["success"]:
        ...     print("Issue updated successfully")
    """
    try:
        jira_client, error = _get_jira_client()
        if error:
            return {
                "success": False,
                "error": error,
                "error_type": "configuration_error",
            }

        # Fetch the issue
        issue = jira_client.issue(issue_key)

        # Get available transitions
        transitions = jira_client.transitions(issue)
        transition_id = None

        # Find the transition ID for the target status
        for transition in transitions:
            if (
                transition["name"].lower() == status.lower()
                or transition["to"]["name"].lower() == status.lower()
            ):
                transition_id = transition["id"]
                break

        if not transition_id:
            available_statuses = [t["to"]["name"] for t in transitions]
            return {
                "success": False,
                "error": (
                    f"Invalid status transition to '{status}'. "
                    f"Available transitions: {', '.join(available_statuses)}"
                ),
                "error_type": "invalid_transition",
            }

        # Perform the transition
        jira_client.transition_issue(issue, transition_id)
        logger.info(f"Transitioned issue {issue_key} to status: {status}")

        # Reassign if assignee is provided
        if assignee:
            try:
                # Try to find user by email or username
                users = jira_client.search_users(assignee)
                if not users:
                    return {
                        "success": False,
                        "error": f"User not found: {assignee}",
                        "error_type": "user_not_found",
                    }

                # Assign to the first matching user
                jira_client.assign_issue(issue, users[0].accountId)
                logger.info(f"Assigned issue {issue_key} to: {assignee}")

            except JIRAError as e:
                logger.error(f"Failed to assign issue {issue_key}: {e}")
                return {
                    "success": False,
                    "error": f"Failed to assign issue: {str(e)}",
                    "error_type": "assignment_error",
                }

        # Fetch updated issue details
        updated_issue = jira_client.issue(issue_key)

        # Extract updated assignee information
        assignee_info = None
        if updated_issue.fields.assignee:
            assignee_info = {
                "name": updated_issue.fields.assignee.displayName,
                "email": getattr(updated_issue.fields.assignee, "emailAddress", None),
            }

        issue_data = {
            "key": updated_issue.key,
            "summary": updated_issue.fields.summary,
            "status": updated_issue.fields.status.name,
            "assignee": assignee_info,
            "updated": updated_issue.fields.updated,
        }

        return {"success": True, "issue": issue_data}

    except JIRAError as e:
        logger.error(f"JIRA error updating issue {issue_key}: {e}")

        if e.status_code == 404:
            return {
                "success": False,
                "error": f"Issue not found: {issue_key}",
                "error_type": "not_found",
            }
        elif e.status_code == 401:
            return {
                "success": False,
                "error": "Authentication failed. Please check your JIRA credentials.",
                "error_type": "authentication_error",
            }
        elif e.status_code == 403:
            return {
                "success": False,
                "error": f"Permission denied to update issue: {issue_key}",
                "error_type": "permission_error",
            }
        else:
            return {
                "success": False,
                "error": f"JIRA error: {str(e)}",
                "error_type": "jira_error",
            }

    except Exception as e:
        logger.error(f"Unexpected error updating issue {issue_key}: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown",
        }


def add_jira_comment(issue_key: str, comment: str) -> Dict[str, Any]:
    """
    Add a comment to a JIRA issue.

    Args:
        issue_key: JIRA issue key (e.g., "PROJ-123")
        comment: Comment text (supports JIRA markdown)

    Returns:
        dict with keys:
            - success: bool
            - comment: dict (if success=True) with fields:
                - id, body, author, created
            - error: str (if success=False)
            - error_type: str (if success=False)

    Example:
        >>> result = add_jira_comment("PROJ-123", "Updated implementation")
        >>> if result["success"]:
        ...     print(f"Comment added: {result['comment']['id']}")
    """
    try:
        jira_client, error = _get_jira_client()
        if error:
            return {
                "success": False,
                "error": error,
                "error_type": "configuration_error",
            }

        # Add comment to the issue
        new_comment = jira_client.add_comment(issue_key, comment)

        comment_data = {
            "id": new_comment.id,
            "body": new_comment.body,
            "author": new_comment.author.displayName,
            "created": new_comment.created,
        }

        logger.info(f"Successfully added comment to issue: {issue_key}")
        return {"success": True, "comment": comment_data}

    except JIRAError as e:
        logger.error(f"JIRA error adding comment to {issue_key}: {e}")

        if e.status_code == 404:
            return {
                "success": False,
                "error": f"Issue not found: {issue_key}",
                "error_type": "not_found",
            }
        elif e.status_code == 401:
            return {
                "success": False,
                "error": "Authentication failed. Please check your JIRA credentials.",
                "error_type": "authentication_error",
            }
        elif e.status_code == 403:
            return {
                "success": False,
                "error": f"Permission denied to add comment to issue: {issue_key}",
                "error_type": "permission_error",
            }
        else:
            return {
                "success": False,
                "error": f"JIRA error: {str(e)}",
                "error_type": "jira_error",
            }

    except Exception as e:
        logger.error(f"Unexpected error adding comment to {issue_key}: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown",
        }


def create_jira_issue(
    project: str,
    summary: str,
    description: str,
    issue_type: str = "Task",
    assignee: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[List[str]] = None,
    components: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create a new JIRA issue in the specified project.

    Args:
        project: Project key (e.g., "PROJ", "KARA")
        summary: Issue title/summary (required)
        description: Issue description text (required)
        issue_type: Issue type - "Bug", "Story", "Task", "Epic" (default: "Task")
        assignee: Optional username or email to assign issue to
        priority: Optional priority - "Highest", "High", "Medium", "Low", "Lowest"
        labels: Optional list of labels to add
        components: Optional list of component names

    Returns:
        dict with keys:
            - success: bool
            - issue: dict (if success=True) with fields:
                - key: Issue key (e.g., "PROJ-456")
                - url: Direct URL to the issue
                - summary, description, issue_type, status, assignee, priority, labels, components
            - error: str (if success=False)
            - error_type: str (if success=False)

    Example:
        >>> result = create_jira_issue("PROJ", "Fix login bug", "Users cannot login with SSO")
        >>> if result["success"]:
        ...     print(f"Created issue: {result['issue']['key']}")

        >>> result = create_jira_issue(
        ...     project="PROJ",
        ...     summary="Critical security vulnerability",
        ...     description="SQL injection found in user input",
        ...     issue_type="Bug",
        ...     assignee="security-team@example.com",
        ...     priority="Highest",
        ...     labels=["security", "urgent"],
        ...     components=["Backend", "API"]
        ... )
    """
    try:
        # Validate required fields
        validation_errors = []
        if not project or not project.strip():
            validation_errors.append("Project key is required")
        if not summary or not summary.strip():
            validation_errors.append("Summary is required")
        if not description or not description.strip():
            validation_errors.append("Description is required")

        if validation_errors:
            return {
                "success": False,
                "error": "; ".join(validation_errors),
                "error_type": "validation_error",
            }

        # Validate issue type
        valid_issue_types = ["Bug", "Story", "Task", "Epic"]
        if issue_type not in valid_issue_types:
            return {
                "success": False,
                "error": (
                    f"Invalid issue type: {issue_type}. "
                    f"Valid types: {', '.join(valid_issue_types)}"
                ),
                "error_type": "invalid_issue_type",
            }

        # Get JIRA client
        jira_client, error = _get_jira_client()
        if error:
            return {
                "success": False,
                "error": error,
                "error_type": "configuration_error",
            }

        # Get base URL for constructing issue URL
        config = AssistantConfig()
        base_url = config.get_option("jira", "base_url")

        # Build fields dictionary for JIRA API
        fields = {
            "project": {"key": project},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }

        # Add optional priority
        if priority:
            valid_priorities = ["Highest", "High", "Medium", "Low", "Lowest"]
            if priority not in valid_priorities:
                return {
                    "success": False,
                    "error": (
                        f"Invalid priority: {priority}. "
                        f"Valid priorities: {', '.join(valid_priorities)}"
                    ),
                    "error_type": "validation_error",
                }
            fields["priority"] = {"name": priority}

        # Add optional labels
        if labels:
            fields["labels"] = labels

        # Add optional components
        if components:
            fields["components"] = [{"name": comp} for comp in components]

        # Create the issue
        try:
            issue = jira_client.create_issue(fields=fields)
            logger.info(
                f"Successfully created JIRA issue: {issue.key} (type: {issue_type}, project: {project})"
            )
        except JIRAError as e:
            logger.error(f"JIRA error creating issue in project {project}: {e}")

            # Handle specific JIRA errors
            if e.status_code == 404:
                return {
                    "success": False,
                    "error": f"Project not found: {project}",
                    "error_type": "project_not_found",
                }
            elif e.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication failed. Please check your JIRA credentials.",
                    "error_type": "authentication_error",
                }
            elif e.status_code == 403:
                return {
                    "success": False,
                    "error": f"Permission denied to create issues in project: {project}",
                    "error_type": "permission_error",
                }
            elif e.status_code == 400:
                # Bad request - could be invalid component, invalid field, etc.
                error_msg = str(e)
                if "component" in error_msg.lower():
                    return {
                        "success": False,
                        "error": f"Invalid component name. Error: {error_msg}",
                        "error_type": "validation_error",
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Invalid request: {error_msg}",
                        "error_type": "validation_error",
                    }
            else:
                return {
                    "success": False,
                    "error": f"JIRA error: {str(e)}",
                    "error_type": "jira_error",
                }

        # Handle assignee if provided
        if assignee:
            try:
                users = jira_client.search_users(assignee)
                if not users:
                    # Issue was created but assignment failed
                    logger.warning(
                        f"Issue {issue.key} created but user not found: {assignee}"
                    )
                    return {
                        "success": False,
                        "error": f"Issue created as {issue.key}, but user not found: {assignee}",
                        "error_type": "user_not_found",
                    }

                # Assign to the first matching user
                jira_client.assign_issue(issue, users[0].accountId)
                logger.info(f"Assigned issue {issue.key} to: {assignee}")

            except JIRAError as e:
                logger.error(f"Failed to assign issue {issue.key}: {e}")
                return {
                    "success": False,
                    "error": f"Issue created as {issue.key}, but failed to assign: {str(e)}",
                    "error_type": "assignment_error",
                }

        # Fetch complete issue details
        created_issue = jira_client.issue(issue.key)

        # Extract assignee information
        assignee_info = None
        if created_issue.fields.assignee:
            assignee_info = {
                "name": created_issue.fields.assignee.displayName,
                "email": getattr(created_issue.fields.assignee, "emailAddress", None),
            }

        # Extract reporter information
        reporter_info = None
        if created_issue.fields.reporter:
            reporter_info = {
                "name": created_issue.fields.reporter.displayName,
                "email": getattr(created_issue.fields.reporter, "emailAddress", None),
            }

        # Extract priority
        priority_name = None
        if hasattr(created_issue.fields, "priority") and created_issue.fields.priority:
            priority_name = created_issue.fields.priority.name

        # Extract labels
        labels_list = []
        if hasattr(created_issue.fields, "labels") and created_issue.fields.labels:
            labels_list = created_issue.fields.labels

        # Extract components
        components_list = []
        if (
            hasattr(created_issue.fields, "components")
            and created_issue.fields.components
        ):
            components_list = [comp.name for comp in created_issue.fields.components]

        # Build response
        issue_data = {
            "key": created_issue.key,
            "url": f"{base_url}/browse/{created_issue.key}",
            "summary": created_issue.fields.summary,
            "description": created_issue.fields.description or "",
            "issue_type": created_issue.fields.issuetype.name,
            "status": created_issue.fields.status.name,
            "assignee": assignee_info,
            "priority": priority_name,
            "labels": labels_list,
            "components": components_list,
            "created": created_issue.fields.created,
            "reporter": reporter_info,
        }

        return {"success": True, "issue": issue_data}

    except Exception as e:
        logger.error(f"Unexpected error creating issue in project {project}: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unknown",
        }
