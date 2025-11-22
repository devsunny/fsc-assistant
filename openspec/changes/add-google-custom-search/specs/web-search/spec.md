## ADDED Requirements

### Requirement: Google Custom Search API Integration
The system SHALL provide a tool function to search using Google's Custom Search JSON API as a more reliable alternative to web scraping.

#### Scenario: Successful search with API credentials
- **GIVEN** valid Google Custom Search API credentials (api_key and search_engine_id) are configured
- **WHEN** the search_google_custom_api function is called with a search query
- **THEN** the function SHALL return search results from Google's official API
- **AND** the results SHALL include titles, snippets, and URLs for each result
- **AND** the function SHALL format the output as a markdown document with proper attribution

#### Scenario: Search with custom number of results
- **GIVEN** valid Google Custom Search API credentials are configured
- **WHEN** the search_google_custom_api function is called with a query and custom num_results parameter
- **THEN** the function SHALL return the specified number of search results (up to 10)
- **AND** the results SHALL be properly formatted in markdown

#### Scenario: Search with safe search filtering
- **GIVEN** valid Google Custom Search API credentials are configured
- **WHEN** the search_google_custom_api function is called with safe_search parameter
- **THEN** the function SHALL apply the appropriate safe search filtering level
- **AND** the results SHALL respect the safe search setting

#### Scenario: Fallback when API credentials are missing
- **GIVEN** Google Custom Search API credentials are not configured
- **WHEN** the search_google_custom_api function is called
- **THEN** the function SHALL detect missing credentials
- **AND** the function SHALL return a clear error message indicating missing configuration
- **AND** the error message SHALL include instructions on how to obtain and configure the credentials

#### Scenario: API quota exceeded
- **GIVEN** valid Google Custom Search API credentials are configured
- **AND** the API quota has been exceeded
- **WHEN** the search_google_custom_api function is called
- **THEN** the function SHALL handle the API quota error gracefully
- **AND** the function SHALL return an error message indicating quota exhaustion
- **AND** the error message SHALL include guidance on quota limits and upgrade options

#### Scenario: Invalid API credentials
- **GIVEN** Google Custom Search API credentials are configured but invalid
- **WHEN** the search_google_custom_api function is called
- **THEN** the function SHALL handle authentication errors from the API
- **AND** the function SHALL return an error message indicating invalid credentials
- **AND** the error message SHALL suggest verifying the api_key and search_engine_id

#### Scenario: Search with site restriction
- **GIVEN** valid Google Custom Search API credentials are configured
- **WHEN** the search_google_custom_api function is called with a site_restrict parameter
- **THEN** the function SHALL restrict search results to the specified site(s)
- **AND** the function SHALL return only results from the restricted site(s)

#### Scenario: Search result formatting
- **GIVEN** valid Google Custom Search API credentials are configured
- **AND** a search returns multiple results
- **WHEN** the search_google_custom_api function is called
- **THEN** the function SHALL format results as a markdown document
- **AND** the document SHALL include a header with the search query
- **AND** each result SHALL include title, snippet, and URL
- **AND** results SHALL be numbered sequentially

### Requirement: Google API Configuration Management
The system SHALL provide configuration management for Google Custom Search API credentials through the AssistantConfig system.

#### Scenario: Configuration section initialization
- **GIVEN** the AssistantConfig is initialized
- **WHEN** the configuration is loaded or created
- **THEN** the system SHALL include a 'google' section with default values
- **AND** the section SHALL contain 'api_key' and 'search_engine_id' keys with empty string defaults

#### Scenario: Setting Google API configuration
- **GIVEN** a user wants to configure Google Custom Search API
- **WHEN** the user sets values for google.api_key and google.search_engine_id
- **THEN** the configuration system SHALL persist these values
- **AND** the values SHALL be available to the search_google_custom_api function

#### Scenario: Retrieving Google API configuration
- **GIVEN** Google API credentials are stored in configuration
- **WHEN** the search_google_custom_api function retrieves the configuration
- **THEN** the function SHALL obtain the api_key and search_engine_id values
- **AND** the function SHALL use these values for API authentication

### Requirement: Dependency Management
The system SHALL manage the google-api-python-client dependency appropriately.

#### Scenario: Dependency availability check
- **GIVEN** the search_google_custom_api function is called
- **WHEN** the function attempts to import the google-api-python-client
- **THEN** the function SHALL check if the dependency is available
- **AND** if not available, the function SHALL return an error message with installation instructions

#### Scenario: Graceful degradation
- **GIVEN** the google-api-python-client dependency is not installed
- **WHEN** the search_google_custom_api function is called
- **THEN** the function SHALL not crash the application
- **AND** the function SHALL provide clear guidance on installing the required dependency