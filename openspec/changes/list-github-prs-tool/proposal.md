# List GitHub Pull Requests Tool Function

## Overview

This change proposes adding a new tool function to list GitHub pull requests using the GitHub API. This functionality would complement the existing `create_github_pull_request` and `close_github_pull_request` functions by providing the ability to retrieve and list PRs programmatically.

## Problem Statement

Currently, the assistant can create and close pull requests but cannot list or retrieve existing PRs. Users may need to:
- View all open PRs in a repository
- Check the status of specific PRs
- Get PR details for automation workflows
- Review PR history and metadata

## Solution

Add a new tool function `list_github_pull_requests` that allows retrieving GitHub pull requests with filtering options for state (open, closed, all), sorting, and pagination.

## Requirements

### ADDED Requirements

#### Scenario: List all open pull requests
- Given I have a valid GitHub API token configured
- And I know the repository owner/repo format
- When I execute the list_github_pull_requests tool with state="open"
- Then all open PRs should be returned with their details

#### Scenario: List closed pull requests
- Given I have a valid GitHub API token configured
- And I know the repository owner/repo format
- When I execute the list_github_pull_requests tool with state="closed"
- Then all closed PRs should be returned with their details

#### Scenario: List all pull requests (open and closed)
- Given I have a valid GitHub API token configured
- And I know the repository owner/repo format
- When I execute the list_github_pull_requests tool with state="all"
- Then all PRs should be returned with their details

#### Scenario: List pull requests with invalid authentication
- Given I don't have valid GitHub API token configured
- When I attempt to list pull requests
- Then an authentication error should be returned

#### Scenario: List pull requests from non-existent repository
- Given I have a valid GitHub API token configured
- And I provide a repository that doesn't exist
- When I execute the list_github_pull_requests tool
- Then an appropriate error message should be returned

## Implementation Plan

1. Create a new function `list_github_pull_requests` in the GitHub integration module
2. Add support for filtering by state (open, closed, all)
3. Add support for sorting and pagination parameters
4. Implement proper validation for repository format
5. Implement comprehensive error handling for GitHub API responses
6. Ensure consistent return structure with existing functions
7. Add appropriate logging and documentation

## Acceptance Criteria

- Function accepts repository owner/repo format or uses default_owner from config
- Function supports filtering by PR state (open, closed, all)
- Function supports sorting options (created, updated, popularity, etc.)
- Function supports pagination parameters
- Function properly handles authentication errors
- Function returns structured response similar to other GitHub functions
- Function handles cases where repository doesn't exist gracefully
- All existing functionality remains unchanged