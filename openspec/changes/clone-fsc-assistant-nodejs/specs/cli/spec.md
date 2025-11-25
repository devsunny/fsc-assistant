# CLI Interface Specification

## ADDED Requirements

### Requirement: Command Line Interface
The system SHALL provide a command-line interface that allows users to start an interactive shell with `fsc` or `fsc-assistant`.

#### Scenario:
The Node.js version of FSC Assistant must provide the same command-line interface as the Python version, allowing users to start an interactive shell with `fsc` or `fsc-assistant`.

#### Scenario:
The CLI should support configuration file path specification using `-c` or `--config` flag.

### Requirement: Help and Documentation
The system SHALL display usage information when running `fsc --help`.

#### Scenario:
Running `fsc --help` should display usage information including available options and commands.

## MODIFIED Requirements

### Requirement: Interactive Shell Entry Point
The system SHALL start an interactive shell session when invoked without arguments, matching Python behavior.

#### Scenario:
When invoked without arguments, the CLI should start an interactive shell session that behaves identically to the Python version.

#### Scenario:
The interactive shell must support multi-line input for complex queries.

## REMOVED Requirements

No requirements are removed in this change.