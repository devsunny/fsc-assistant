import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Import BaseTool from the new location
from .base_tool import BaseTool


def create_jira_issue(project: str, summary: str, description: str, issue_type: str = "Task",
                     assignee: Optional[str] = None, priority: Optional[str] = None,
                     labels: Optional[List[str]] = None, components: Optional[List[str]] = None) -> dict:
    """
    Create a new JIRA issue in the specified project.
    
    Parameters
    ----------
    project : str
        Project key (e.g., "PROJ", "KARA")
    summary : str
        Issue title/summary (required)
    description : str
        Issue description text (required)
    issue_type : str, optional
        Issue type - "Bug", "Story", "Task", "Epic" (default: "Task")
    assignee : str, optional
        Optional username or email to assign issue to
    priority : str, optional
        Optional priority - "Highest", "High", "Medium", "Low", "Lowest"
    labels : list of str, optional
        Optional list of labels to add
    components : list of str, optional
        Optional list of component names
        
    Returns
    -------
    dict
        Created issue details or error information
    """
    logger.info(f"Creating JIRA issue in project {project}: {summary}")
    
    # In a real implementation, this would actually create the JIRA issue
    # For now we'll return placeholder data  
    return {
        "issue_key": f"{project}-123",
        "project": project,
        "summary": summary,
        "description": description,
        "type": issue_type
    }


def update_jira_issue_status(issue_key: str, status: str, assignee: Optional[str] = None) -> dict:
    """
    Update JIRA issue status and optionally reassign.
    
    Parameters
    ----------
    issue_key : str
        JIRA issue key (e.g., "PROJ-123")
    status : str
        Target status (e.g., "In Progress", "Done", "QA")
    assignee : str, optional
        Optional username or email to assign issue to
        
    Returns
    -------
    dict
        Update result or error information
    """
    logger.info(f"Updating JIRA issue {issue_key} status to: {status}")
    
    # In a real implementation, this would actually update the JIRA issue  
    # For now we'll return placeholder data
    return {
        "issue_key": issue_key,
        "status": status,
        "updated": True
    }


def add_jira_comment(issue_key: str, comment: str) -> dict:
    """
    Add a comment to a JIRA issue.
    
    Parameters
    ----------
    issue_key : str
        JIRA issue key (e.g., "PROJ-123")
    comment : str
        Comment text (supports JIRA markdown)
        
    Returns
    -------
    dict
        Comment addition result or error information
    """
    logger.info(f"Adding comment to JIRA issue {issue_key}")
    
    # In a real implementation, this would actually add the comment
    # For now we'll return placeholder data
    return {
        "issue_key": issue_key,
        "comment_added": True,
        "comment_text": comment[:50] + ("..." if len(comment) > 50 else "")
    }


# Tool class that extends BaseTool
class CreateJiraIssueTool(BaseTool):
    """A tool for creating new JIRA issues."""
    
    name = "create_jira_issue"
    description = "Create a new JIRA issue in the specified project"
    parameters = {
        "project": {
            "type": "string",
            "description": "Project key (e.g., \"PROJ\", \"KARA\")",
            "required": True
        },
        "summary": {
            "type": "string",
            "description": "Issue title/summary (required)",
            "required": True
        },
        "description": {
            "type": "string", 
            "description": "Issue description text (required)",
            "required": True
        }
    }

    def __init__(self, config=None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> dict:
        """
        Execute creating a JIRA issue.
        
        Parameters:
            **kwargs: 
                project (str): Project key  
                summary (str): Issue title/summary
                description (str): Issue description text
                
        Returns:
            dict: Created issue details or error information
        """
        try:
            project = kwargs.get("project")
            summary = kwargs.get("summary") 
            description = kwargs.get("description")
            
            if not project or not summary or not description:
                return {
                    "success": False,
                    "error": "Missing required parameters",
                    "message": "Please provide project, summary, and description"
                }
                
            result = create_jira_issue(project, summary, description)
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": "JIRA issue creation failed",
                "message": f"Failed to create JIRA issue: {str(e)}"
            }


# Tool class that extends BaseTool  
class UpdateJiraIssueStatusTool(BaseTool):
    """A tool for updating JIRA issue status."""
    
    name = "update_jira_issue_status"
    description = "Update JIRA issue status and optionally reassign"
    parameters = {
        "issue_key": {
            "type": "string",
            "description": "JIRA issue key (e.g., \"PROJ-123\")",
            "required": True
        },
        "status": {
            "type": "string",
            "description": "Target status (e.g., \"In Progress\", \"Done\", \"QA\")",
            "required": True
        }
    }

    def __init__(self, config=None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> dict:
        """
        Execute updating JIRA issue status.
        
        Parameters:
            **kwargs: 
                issue_key (str): JIRA issue key
                status (str): Target status
                
        Returns:
            dict: Update result or error information
        """
        try:
            issue_key = kwargs.get("issue_key")
            status = kwargs.get("status")
            
            if not issue_key or not status:
                return {
                    "success": False,
                    "error": "Missing required parameters",
                    "message": "Please provide both issue key and status"
                }
                
            result = update_jira_issue_status(issue_key, status)
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": "JIRA status update failed",
                "message": f"Failed to update JIRA issue status: {str(e)}"
            }


# Tool class that extends BaseTool  
class AddJiraCommentTool(BaseTool):
    """A tool for adding comments to JIRA issues."""
    
    name = "add_jira_comment"
    description = "Add a comment to a JIRA issue"
    parameters = {
        "issue_key": {
            "type": "string",
            "description": "JIRA issue key (e.g., \"PROJ-123\")",
            "required": True
        },
        "comment": {
            "type": "string",
            "description": "Comment text (supports JIRA markdown)",
            "required": True
        }
    }

    def __init__(self, config=None):
        super().__init__(config)
        
    def execute(self, **kwargs) -> dict:
        """
        Execute adding a comment to a JIRA issue.
        
        Parameters:
            **kwargs: 
                issue_key (str): JIRA issue key
                comment (str): Comment text
                
        Returns:
            dict: Comment addition result or error information
        """
        try:
            issue_key = kwargs.get("issue_key")
            comment = kwargs.get("comment")
            
            if not issue_key or not comment:
                return {
                    "success": False,
                    "error": "Missing required parameters",
                    "message": "Please provide both issue key and comment"
                }
                
            result = add_jira_comment(issue_key, comment)
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": "JIRA comment addition failed",
                "message": f"Failed to add JIRA comment: {str(e)}"
            }


# Tool registry for automatic discovery
TOOL_REGISTRY = [
    CreateJiraIssueTool,
    UpdateJiraIssueStatusTool,
    AddJiraCommentTool
]