# Version Update Specification

## ADDED Requirements

### Requirement: Update pyproject.toml version
The system SHALL update the version in pyproject.toml from 0.1.4 to 0.1.5.

#### Scenario: Update pyproject.toml version
- Given the current pyproject.toml file contains `version = "0.1.4"`
- When the version is updated to `0.1.5`
- Then the pyproject.toml should contain `version = "0.1.5"`

### Requirement: Update __version__.py version  
The system SHALL update the version in src/assistant/__version__.py from 0.1.4 to 0.1.5.

#### Scenario: Update __version__.py version
- Given the current src/assistant/__version__.py file contains `__version__ = "0.1.4"`
- When the version is updated to `0.1.5`
- Then the __version__.py should contain `__version__ = "0.1.5"`

## MODIFIED Requirements

### Requirement: All version references are consistent
The system SHALL ensure all version references in the codebase are updated consistently.

#### Scenario: All version references are consistent
- Given multiple files contain version information
- When all version references are updated to 0.1.5
- Then all references should be identical and point to the same version number

## REMOVED Requirements

No requirements removed.