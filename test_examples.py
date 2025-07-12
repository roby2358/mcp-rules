#!/usr/bin/env python3
"""
Test examples for MCP Rules Engine Wrapper

This script demonstrates how to use the rules engine functionality
directly (without MCP) for testing and development purposes.
"""

import json
from mcp_rules_engine import RulesEngine, ActionExecutor, RuleDefinition, mcp


def test_simple_rule():
    """Test a simple rule evaluation"""
    print("=== Testing Simple Rule ===")
    
    engine = RulesEngine()
    
    # Simple age check rule
    rule = {">": [{"var": "age"}, 18]}
    data = {"age": 25}
    
    matched, error = engine.evaluate_rule(rule, data)
    print(f"Rule: {rule}")
    print(f"Data: {data}")
    print(f"Matched: {matched}")
    print(f"Error: {error}")
    print()


def test_complex_rule():
    """Test a complex rule with multiple conditions"""
    print("=== Testing Complex Rule ===")
    
    engine = RulesEngine()
    
    # Complex rule: VIP customer check
    rule = {
        "and": [
            {"or": [
                {"==": [{"var": "user.tier"}, "platinum"]},
                {">": [{"var": "user.lifetime_value"}, 10000]}
            ]},
            {">": [{"var": "order.total"}, 500]}
        ]
    }
    
    data = {
        "user": {
            "tier": "gold",
            "lifetime_value": 15000
        },
        "order": {
            "total": 750
        }
    }
    
    matched, error = engine.evaluate_rule(rule, data)
    print(f"Rule: {json.dumps(rule, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print(f"Matched: {matched}")
    print(f"Error: {error}")
    print()


def test_ruleset_evaluation():
    """Test evaluating multiple rules"""
    print("=== Testing Ruleset Evaluation ===")
    
    engine = RulesEngine()
    
    # Define multiple rules
    rules = [
        RuleDefinition(
            name="high_value_order",
            description="Detect high-value orders",
            rule={">": [{"var": "order.total"}, 1000]},
            actions=["NotificationActions.send_email"]
        ),
        RuleDefinition(
            name="vip_customer",
            description="VIP customer check",
            rule={"==": [{"var": "user.tier"}, "platinum"]},
            actions=["BusinessActions.apply_discount"]
        ),
        RuleDefinition(
            name="bulk_order",
            description="Bulk order check",
            rule={">": [{"var": "order.quantity"}, 50]},
            actions=["BusinessActions.apply_discount"]
        )
    ]
    
    data = {
        "order": {
            "total": 1500,
            "quantity": 75
        },
        "user": {
            "tier": "gold"
        }
    }
    
    results = engine.evaluate_ruleset(rules, data)
    
    print(f"Data: {json.dumps(data, indent=2)}")
    print("Results:")
    for result in results:
        print(f"  {result.rule_name}: {result.matched} ({result.execution_time_ms:.2f}ms)")
        if result.error:
            print(f"    Error: {result.error}")
    print()


def test_action_execution():
    """Test action execution"""
    print("=== Testing Action Execution ===")
    
    executor = ActionExecutor()
    
    data = {
        "user": {"name": "John Doe", "email": "john@example.com"},
        "order": {"id": "ORD-123", "total": 1500}
    }
    
    # Test single action
    result = executor.execute_action("NotificationActions.send_email", data)
    print(f"Action: NotificationActions.send_email")
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")
    print(f"Execution time: {result.execution_time_ms:.2f}ms")
    if result.error:
        print(f"Error: {result.error}")
    print()


def test_rule_validation():
    """Test rule validation"""
    print("=== Testing Rule Validation ===")
    
    engine = RulesEngine()
    
    # Valid rule
    valid_rule = {">": [{"var": "age"}, 18]}
    is_valid, error = engine.validate_rule(valid_rule)
    print(f"Valid rule: {valid_rule}")
    print(f"Is valid: {is_valid}")
    print(f"Error: {error}")
    print()
    
    # Invalid rule
    invalid_rule = {"invalid_operator": [{"var": "age"}, 18]}
    is_valid, error = engine.validate_rule(invalid_rule)
    print(f"Invalid rule: {invalid_rule}")
    print(f"Is valid: {is_valid}")
    print(f"Error: {error}")
    print()


def test_example_rules():
    """Test rules from example_rules.json"""
    print("=== Testing Example Rules ===")
    
    engine = RulesEngine()
    executor = ActionExecutor()
    
    # Load example rules
    with open('example_rules.json', 'r') as f:
        config = json.load(f)
    
    # Convert to RuleDefinition objects
    rules = []
    for rule_data in config['rules']:
        rule_def = RuleDefinition(**rule_data)
        rules.append(rule_def)
    
    # Test data scenarios
    test_scenarios = [
        {
            "name": "High Value Order",
            "data": {
                "order": {"total": 1500, "quantity": 10},
                "user": {"tier": "gold", "email": "customer@example.com"}
            }
        },
        {
            "name": "Suspicious Login",
            "data": {
                "login": {"country": "RU", "failed_attempts": 5},
                "user": {"home_country": "US", "phone": "+1234567890"}
            }
        },
        {
            "name": "VIP Customer",
            "data": {
                "user": {"tier": "platinum", "lifetime_value": 15000, "email": "vip@example.com"},
                "order": {"total": 500}
            }
        },
        {
            "name": "Fraud Detection",
            "data": {
                "transaction": {"amount": 5000, "ip_country": "CN", "card_number": "1234567890123456"},
                "user": {"daily_limit": 2000, "country": "US"},
                "blacklist": {"cards": ["1234567890123456", "9876543210987654"]}
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"--- {scenario['name']} ---")
        results = engine.evaluate_ruleset(rules, scenario['data'])
        
        matched_rules = [r for r in results if r.matched]
        print(f"Matched rules: {len(matched_rules)}")
        
        for result in matched_rules:
            print(f"  ✓ {result.rule_name} ({result.execution_time_ms:.2f}ms)")
            
            # Find the rule definition to get actions
            rule_def = next((r for r in rules if r.name == result.rule_name), None)
            if rule_def and rule_def.actions:
                print(f"    Actions: {', '.join(rule_def.actions)}")
                
                # Execute actions (mock)
                for action in rule_def.actions:
                    action_result = executor.execute_action(action, scenario['data'])
                    print(f"      → {action}: {'✓' if action_result.success else '✗'}")
        
        print()


async def test_fastmcp_client():
    """Test using FastMCP client for testing"""
    print("=== Testing FastMCP Client ===")
    
    from fastmcp import Client
    
    # Test using in-memory client
    async with Client(mcp) as client:
        # Test evaluate_rule tool
        result = await client.call_tool("evaluate_rule", {
            "rule": {">": [{"var": "age"}, 18]},
            "data": {"age": 25}
        })
        print(f"Client result: {result}")
        
        # Test validate_rule tool
        validation_result = await client.call_tool("validate_rule", {
            "rule": {">": [{"var": "age"}, 18]},
            "actions": ["NotificationActions.send_email"]
        })
        print(f"Validation result: {validation_result}")
    
    print()


if __name__ == "__main__":
    test_simple_rule()
    test_complex_rule()
    test_ruleset_evaluation()
    test_action_execution()
    test_rule_validation()
    test_example_rules()
    
    # Test FastMCP client (requires async)
    import asyncio
    asyncio.run(test_fastmcp_client()) 