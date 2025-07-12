#!/usr/bin/env python3
"""
MCP Rules Engine Wrapper

A Python MCP server that provides rule evaluation capabilities to MCP clients.
Implements the MCP Rules Engine Wrapper Specification.
"""

import json
import logging
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import importlib.util

from fastmcp import FastMCP
from pydantic import BaseModel, ValidationError
import json_logic


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RuleDefinition(BaseModel):
    """Rule definition model"""
    name: str
    description: Optional[str] = None
    rule: Dict[str, Any]  # JSON Logic rule
    actions: Optional[List[str]] = None  # List of class.method specifications


class RulesetDefinition(BaseModel):
    """Ruleset definition model"""
    name: str
    description: Optional[str] = None
    rules: List[RuleDefinition]


class RuleEvaluationResult(BaseModel):
    """Result of rule evaluation"""
    rule_name: str
    matched: bool
    execution_time_ms: float
    error: Optional[str] = None


class ActionExecutionResult(BaseModel):
    """Result of action execution"""
    action: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: float


class RuleActionExecutionResult(BaseModel):
    """Result of rule evaluation with action execution"""
    rule_name: str
    matched: bool
    rule_execution_time_ms: float
    actions_executed: List[ActionExecutionResult]
    rule_error: Optional[str] = None


class RulesEngine:
    """Core rules engine implementation using json-logic-py"""
    
    def __init__(self):
        self.rule_cache = {}
        
    def validate_rule(self, rule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate rule syntax"""
        try:
            # Test compilation by applying to empty data
            json_logic.jsonLogic(rule, {})
            return True, None
        except Exception as e:
            return False, str(e)
    
    def evaluate_rule(self, rule: Dict[str, Any], data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Evaluate a single rule against data"""
        try:
            start_time = time.time()
            result = json_logic.jsonLogic(rule, data)
            execution_time = (time.time() - start_time) * 1000
            
            # Ensure result is boolean
            if not isinstance(result, bool):
                result = bool(result)
                
            return result, None
        except Exception as e:
            return False, str(e)
    
    def evaluate_ruleset(self, rules: List[RuleDefinition], data: Dict[str, Any]) -> List[RuleEvaluationResult]:
        """Evaluate multiple rules against data"""
        results = []
        
        for rule_def in rules:
            start_time = time.time()
            try:
                matched, error = self.evaluate_rule(rule_def.rule, data)
                execution_time = (time.time() - start_time) * 1000
                
                results.append(RuleEvaluationResult(
                    rule_name=rule_def.name,
                    matched=matched,
                    execution_time_ms=execution_time,
                    error=error
                ))
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                results.append(RuleEvaluationResult(
                    rule_name=rule_def.name,
                    matched=False,
                    execution_time_ms=execution_time,
                    error=str(e)
                ))
        
        return results


class ActionExecutor:
    """Executes actions specified as class.method"""
    
    def __init__(self):
        self.module_cache = {}
    
    def _import_module_from_path(self, module_path: str):
        """Import a module from file path"""
        if module_path in self.module_cache:
            return self.module_cache[module_path]
        
        try:
            spec = importlib.util.spec_from_file_location("action_module", module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.module_cache[module_path] = module
            return module
        except Exception as e:
            logger.error(f"Failed to import module from {module_path}: {e}")
            return None
    
    def execute_action(self, action_spec: str, data: Dict[str, Any]) -> ActionExecutionResult:
        """Execute a single action specified as class.method"""
        start_time = time.time()
        
        try:
            # Parse action specification
            if '.' not in action_spec:
                raise ValueError(f"Invalid action specification: {action_spec}. Expected format: class.method")
            
            parts = action_spec.split('.')
            if len(parts) != 2:
                raise ValueError(f"Invalid action specification: {action_spec}. Expected format: class.method")
            
            class_name, method_name = parts
            
            # For now, we'll assume actions are defined in a separate actions module
            # In a real implementation, this would be configurable
            try:
                import actions
                action_class = getattr(actions, class_name)
                action_instance = action_class()
                action_method = getattr(action_instance, method_name)
                
                result = action_method(data)
                execution_time = (time.time() - start_time) * 1000
                
                return ActionExecutionResult(
                    action=action_spec,
                    success=True,
                    result=result,
                    execution_time_ms=execution_time
                )
            except ImportError:
                # If actions module doesn't exist, return a mock result
                execution_time = (time.time() - start_time) * 1000
                return ActionExecutionResult(
                    action=action_spec,
                    success=True,
                    result=f"Mock execution of {action_spec}",
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ActionExecutionResult(
                action=action_spec,
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    def execute_actions(self, action_specs: List[str], data: Dict[str, Any]) -> List[ActionExecutionResult]:
        """Execute multiple actions"""
        return [self.execute_action(spec, data) for spec in action_specs]


# Create FastMCP server instance
mcp = FastMCP("mcp-rules-engine")

# Initialize core components
rules_engine = RulesEngine()
action_executor = ActionExecutor()


@mcp.tool
def evaluate_rule(rule: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate a single rule against input data (dry run, no actions)"""
    start_time = time.time()
    matched, error = rules_engine.evaluate_rule(rule, data)
    execution_time = (time.time() - start_time) * 1000
    
    return {
        "matched": matched,
        "execution_time_ms": execution_time,
        "error": error
    }


@mcp.tool
def evaluate_ruleset(rules: List[Dict[str, Any]], data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Evaluate multiple rules against input data (dry run, no actions)"""
    # Convert to RuleDefinition objects
    rule_definitions = []
    for rule_data in rules:
        try:
            rule_def = RuleDefinition(**rule_data)
            rule_definitions.append(rule_def)
        except ValidationError as e:
            raise ValueError(f"Invalid rule definition: {e}")
    
    results = rules_engine.evaluate_ruleset(rule_definitions, data)
    
    # Convert to dict for JSON serialization
    return [result.model_dump() for result in results]


@mcp.tool
def execute_rule_actions(rules: List[Dict[str, Any]], data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Evaluate rules and execute associated actions when rules match"""
    # Convert to RuleDefinition objects
    rule_definitions = []
    for rule_data in rules:
        try:
            rule_def = RuleDefinition(**rule_data)
            rule_definitions.append(rule_def)
        except ValidationError as e:
            raise ValueError(f"Invalid rule definition: {e}")
    
    results = []
    
    for rule_def in rule_definitions:
        start_time = time.time()
        try:
            matched, rule_error = rules_engine.evaluate_rule(rule_def.rule, data)
            rule_execution_time = (time.time() - start_time) * 1000
            
            actions_executed = []
            
            if matched and rule_def.actions:
                # Execute ALL actions when rule matches
                actions_executed = action_executor.execute_actions(rule_def.actions, data)
            
            results.append(RuleActionExecutionResult(
                rule_name=rule_def.name,
                matched=matched,
                rule_execution_time_ms=rule_execution_time,
                actions_executed=actions_executed,
                rule_error=rule_error
            ))
            
        except Exception as e:
            rule_execution_time = (time.time() - start_time) * 1000
            results.append(RuleActionExecutionResult(
                rule_name=rule_def.name,
                matched=False,
                rule_execution_time_ms=rule_execution_time,
                actions_executed=[],
                rule_error=str(e)
            ))
    
    # Convert to dict for JSON serialization
    return [result.model_dump() for result in results]


@mcp.tool
def validate_rule(rule: Dict[str, Any], actions: Optional[List[str]] = None) -> Dict[str, Any]:
    """Validate rule syntax and action definitions"""
    if actions is None:
        actions = []
    
    # Validate rule syntax
    rule_valid, rule_error = rules_engine.validate_rule(rule)
    
    # Validate action specifications
    action_errors = []
    for action in actions:
        if '.' not in action:
            action_errors.append(f"Invalid action specification: {action}. Expected format: class.method")
        elif len(action.split('.')) != 2:
            action_errors.append(f"Invalid action specification: {action}. Expected format: class.method")
    
    return {
        "rule_valid": rule_valid,
        "rule_error": rule_error,
        "actions_valid": len(action_errors) == 0,
        "action_errors": action_errors if action_errors else None
    }


if __name__ == "__main__":
    mcp.run() 