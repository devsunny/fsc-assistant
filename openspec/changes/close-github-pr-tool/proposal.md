# Close GitHub Pull Request Tool Function

## Overview

This change proposes adding a new tool function to close existing GitHub pull requests using the GitHub API. This functionality would complement the existing `create_github_pull_request` function by providing the ability to close PRs programmatically.

## Problem Statement

Currently, the assistant can create pull requests but cannot close them. Users may need to close PRs for various reasons such as:
- Canceling work in progress
- Closing stale or outdated PRs
- Managing workflow where a PR is created and then closed before merging

## Solution

Add a new tool function `close_github_pull_request` that allows closing existing GitHub pull requests by providing the repository, owner, and PR number.

## Requirements

### ADDED Requirements

#### Scenario: Close an open pull request
- Given I have a valid GitHub API token configured
- And I know the repository owner/repo format
- And I know the pull request number to close
- When I execute the close_github_pull_request tool
- Then the PR should be closed successfully and return confirmation

#### Scenario: Close a pull request that doesn't exist
- Given I have a valid GitHub API token configured
- And I provide a repository and PR number that doesn't exist
- When I execute the close_github_pull_request tool
- Then an appropriate error message should be returned indicating the PR was not found

#### Scenario: Close a pull request with invalid authentication
- Given I don't have valid GitHub API token configured
- When I attempt to close a pull request
- Then an authentication error should be returned

## Implementation Plan

1. Create a new function `close_github_pull_request` in the GitHub integration module
2. Add proper validation for repository format and PR number
3. Implement error handling for various GitHub API responses
4. Ensure consistency with existing tool patterns and error reporting
5. Add appropriate logging and documentation

## Acceptance Criteria

- Function accepts repository owner/repo format or uses default_owner from config
- Function accepts pull request number to close
- Function properly handles authentication errors
- Function returns structured response similar to other GitHub functions
- Function handles cases where PR doesn't exist gracefully
- All existing functionality remains unchanged