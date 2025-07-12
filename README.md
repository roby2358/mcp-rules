# MCP Rules Engine Wrapper

A Python MCP (Model Context Protocol) server that provides rule evaluation capabilities to MCP clients. This implementation follows the MCP Rules Engine Wrapper Specification and uses JSON Logic for rule evaluation.

## Features

- **FastMCP Integration**: Built with FastMCP for simplified MCP server development
- **MCP Protocol Support**: Implements MCP server protocol over stdio (default) or HTTP/SSE
- **Rule Evaluation**: Uses JSON Logic for powerful rule evaluation
- **Action Execution**: Supports rule-action pairs with class.method specifications
- **Validation**: Comprehensive rule and action validation
- **Error Handling**: Graceful error handling with detailed error messages
- **Performance**: Fast rule evaluation with caching support

## Installation

1. Initialize a virtual environment:
```bash
uv venv
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Run the MCP server:
```bash
uv run mcp_rules_engine.py
```

Or using FastMCP's CLI:
```bash
fastmcp run mcp_rules_engine.py
```

## Run in Claude Desktop

To use the MCP Rules Engine with Claude Desktop, add the following configuration to your Claude Desktop settings:

1. Open Claude Desktop settings
2. Navigate to the MCP Servers configuration
3. Add the following entry to your `mcpServers` configuration:

```json
{
  "mcpServers": {
    "mcp-rules-engine": {
      "command": "C:/work/mcp-rules/venv/Scripts/python.exe",
      "args": ["C:/work/mcp-rules/mcp_rules_engine.py"]
    }
  }
}
```

**Note**: Replace the paths with your actual project paths:
- `C:/work/mcp-rules/venv/Scripts/python.exe` - Full path to your virtual environment's Python executable
- `C:/work/mcp-rules/mcp_rules_engine.py` - Full path to the MCP Rules Engine script

For Linux/macOS, the paths would look like:
```json
{
  "mcpServers": {
    "mcp-rules-engine": {
      "command": "/path/to/your/project/venv/bin/python",
      "args": ["/path/to/your/project/mcp_rules_engine.py"]
    }
  }
}
```

After adding this configuration, restart Claude Desktop. The MCP Rules Engine tools will be available in your Claude conversations.

## MCP Tools

The server exposes the following MCP tools:

### evaluate_rule
Evaluate a single rule against input data (dry run, no actions executed).

**Parameters:**
- `rule`: JSON Logic rule definition
- `data`: Input data to evaluate against

**Example:**
```json
{
  "rule": {">": [{"var": "age"}, 18]},
  "data": {"age": 25}
}
```

### evaluate_ruleset
Evaluate multiple rules against input data (dry run, no actions executed).

**Parameters:**
- `rules`: Array of rule definitions
- `data`: Input data to evaluate against

### execute_rule_actions
Evaluate rules and execute associated actions when rules match.

**Parameters:**
- `rules`: Array of rule definitions with actions
- `data`: Input data to evaluate against

### validate_rule
Validate rule syntax and action definitions.

**Parameters:**
- `rule`: JSON Logic rule definition to validate
- `actions`: Optional array of action specifications to validate

## Rule Format

Rules are defined using JSON Logic syntax. Here are some examples:

### Simple Comparison
```json
{
  "rule": {">": [{"var": "age"}, 18]},
  "data": {"age": 25}
}
```

### Complex Logic
```json
{
  "rule": {
    "and": [
      {">": [{"var": "order.total"}, 1000]},
      {"==": [{"var": "user.tier"}, "platinum"]}
    ]
  },
  "data": {
    "order": {"total": 1500},
    "user": {"tier": "platinum"}
  }
}
```

### Nested Field Access
```json
{
  "rule": {"<": [{"var": "user.profile.age"}, 21]},
  "data": {
    "user": {
      "profile": {"age": 19}
    }
  }
}
```

## Action Format

Actions are specified as `class.method` strings and must be defined in the `actions.py` module.

### Example Action Definition
```python
class NotificationActions:
    def send_email(self, data):
        # Send email logic here
        return {"status": "sent", "recipient": data.get("email")}
```

### Example Rule with Actions
```json
{
  "name": "high_value_order",
  "rule": {">": [{"var": "order.total"}, 1000]},
  "actions": [
    "NotificationActions.send_email",
    "BusinessActions.escalate_support"
  ]
}
```

## Example Usage

See `example_rules.json` for comprehensive rule examples covering:
- High-value order detection
- Suspicious login detection
- VIP customer handling
- Inventory management
- Fraud detection
- Age verification
- Bulk discounts
- Support escalation

## Supported Operators

The JSON Logic engine supports all standard operators:

- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical**: `and`, `or`, `not`
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`
- **Array**: `in`, `map`, `filter`, `reduce`
- **String**: `substr`, `cat`
- **Conditional**: `if`

## Error Handling

The server provides comprehensive error handling:
- Malformed rule syntax errors
- Action execution failures
- Validation errors
- Timeout protection
- Detailed error messages

## Performance

- Simple rules evaluate within 100ms
- Rule compilation caching for repeated evaluation
- Concurrent rule evaluation support
- Execution metadata including timing information

## Configuration

Rules and actions can be configured through:
- JSON configuration files
- External storage systems
- Runtime rule definitions (validation only)

Note: Rule management (create, update, delete) is not exposed through MCP tools for security reasons.

## Development

To extend the rules engine:

1. Add new action classes to `actions.py`
2. Define actions as class methods that accept data and return results
3. Reference actions in rules using `ClassName.method_name` format
4. Test rules using the validation tools before deployment 