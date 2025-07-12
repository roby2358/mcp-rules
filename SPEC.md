# MCP Rules Engine Wrapper Specification

## Overview
Python MCP (Model Context Protocol) wrapper that provides rule evaluation capabilities to MCP clients.

## Requirements

### Core Functionality
- MUST implement MCP server protocol over stdio
- MUST provide rule evaluation tools accessible to MCP clients
- MUST support JSON-based rule definitions
- MUST validate rule syntax before execution
- MUST allow user-defined rules and actions via configuration files or external storage
- MUST NOT allow rule or action creation/modification through MCP tools
- SHOULD support multiple rule formats (JSON, YAML)
- MAY support custom rule languages

### Rule Engine
- MUST use a 3rd-party rules engine (not custom implementation)
- MUST evaluate boolean expressions against input data
- MUST support comparison operators (==, !=, <, >, <=, >=)
- MUST support logical operators (AND, OR, NOT)
- MUST support nested conditions
- SHOULD support field path expressions (e.g., `user.profile.age`)
- SHOULD provide rule execution context isolation
- MAY support custom functions in rules

### Rule-Action Bridge
- MUST support rule-action pairs where rules trigger actions when matched
- MUST define actions as class and method specifications
- MUST execute ALL actions when associated rules evaluate to true
- MUST support multiple actions per rule
- MUST NOT support selective action execution (all or nothing)
- MUST NOT support action execution without rule evaluation
- SHOULD provide action execution context isolation
- SHOULD handle action execution failures gracefully

### MCP Tools
- MUST expose `evaluate_rule` tool for single rule evaluation (dry run, no actions)
- MUST expose `evaluate_ruleset` tool for multiple rule evaluation (dry run, no actions)
- MUST expose `execute_rule_actions` tool for rule evaluation with action execution
- MUST expose `validate_rule` tool for rule syntax and action definition validation
- SHOULD expose `list_rules` tool for rule discovery
- MUST NOT expose rule management tools (create, update, delete)

### Input/Output
- MUST accept rule definitions as JSON strings
- MUST accept evaluation data as JSON objects
- MUST accept action definitions as class.method specifications
- MUST return evaluation results as boolean values
- MUST return action execution results when actions are triggered
- MUST return detailed error messages for invalid rules or action failures
- SHOULD return execution metadata (timing, matched conditions, executed actions)

### Error Handling
- MUST handle malformed rule syntax gracefully
- MUST provide clear error messages for rule failures
- MUST prevent rule execution timeouts
- SHOULD log rule evaluation attempts
- MAY provide debugging information for rule execution

### Performance
- MUST evaluate simple rules within 100ms
- SHOULD cache compiled rules for repeated evaluation
- MAY support concurrent rule evaluation

## Implementation Notes
- Use stdio mode for MCP communication
- Implement functional programming patterns where possible
- Keep dependencies minimal
- Ensure all code runs without errors 