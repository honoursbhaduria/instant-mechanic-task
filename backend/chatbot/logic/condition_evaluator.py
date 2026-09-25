"""
Declarative Condition Evaluator for Automotive Diagnostic Rules and Question Relevance.

Evaluates nested declarative rules against an arbitrary facts dictionary without hardcoding.
Supports operators:
  - equals / not_equals
  - contains / not_contains
  - in / not_in
  - exists / not_exists
  - greater_than / less_than
  - Composite operators: all, any, not
"""
from typing import Any, Dict, List, Optional


def get_nested_fact(facts: Dict[str, Any], path: str) -> Any:
    """
    Extract a fact value using dot notation, e.g. 'condition.operating'.
    Checks both direct key ('condition.operating') and nested dictionary traversal ('condition' -> 'operating').
    """
    if not isinstance(facts, dict) or not path:
        return None

    # Check direct match first
    if path in facts:
        return facts[path]

    parts = path.split('.')
    curr: Any = facts
    for part in parts:
        if isinstance(curr, dict) and part in curr:
            curr = curr[part]
        else:
            return None
    return curr


def evaluate_single_rule(rule: Dict[str, Any], facts: Dict[str, Any]) -> bool:
    """
    Evaluates a leaf rule dictionary against the facts dictionary.
    Rule format:
      {"field": "condition.operating", "operator": "equals", "value": "turning"}
      or
      {"field": "condition.operating", "operator": "equals", "expected_value": "turning"}
    """
    field = rule.get("field")
    operator = rule.get("operator", "equals")
    expected = rule.get("expected_value", rule.get("value"))

    if not field:
        return True

    actual = get_nested_fact(facts, field)

    # Existential checks
    if operator == "exists":
        return actual is not None and actual != "" and actual != [] and actual != {}

    if operator == "not_exists":
        return actual is None or actual == "" or actual == [] or actual == {}

    # If actual is None, cannot match positive assertions
    if actual is None:
        return False

    # Normalize strings for comparison
    actual_norm = actual.lower().strip() if isinstance(actual, str) else actual

    if operator == "equals":
        if isinstance(actual_norm, str) and isinstance(expected, str):
            return actual_norm == expected.lower().strip()
        return actual == expected

    elif operator == "not_equals":
        if isinstance(actual_norm, str) and isinstance(expected, str):
            return actual_norm != expected.lower().strip()
        return actual != expected

    elif operator == "in":
        if isinstance(expected, (list, tuple, set)):
            exp_set = {x.lower().strip() if isinstance(x, str) else x for x in expected}
            return actual_norm in exp_set
        elif isinstance(expected, str) and isinstance(actual_norm, str):
            return actual_norm in expected.lower().strip()
        return False

    elif operator == "not_in":
        if isinstance(expected, (list, tuple, set)):
            exp_set = {x.lower().strip() if isinstance(x, str) else x for x in expected}
            return actual_norm not in exp_set
        elif isinstance(expected, str) and isinstance(actual_norm, str):
            return actual_norm not in expected.lower().strip()
        return True

    elif operator == "contains":
        if isinstance(actual, (list, tuple, set)):
            exp_norm = expected.lower().strip() if isinstance(expected, str) else expected
            return any((x.lower().strip() if isinstance(x, str) else x) == exp_norm for x in actual)
        elif isinstance(actual, str) and isinstance(expected, str):
            return expected.lower().strip() in actual.lower().strip()
        return False

    elif operator == "not_contains":
        return not evaluate_single_rule({**rule, "operator": "contains"}, facts)

    elif operator == "greater_than":
        try:
            return float(actual) > float(expected)
        except (ValueError, TypeError):
            return False

    elif operator == "less_than":
        try:
            return float(actual) < float(expected)
        except (ValueError, TypeError):
            return False

    return False


def evaluate_condition(rule: Optional[Dict[str, Any]], facts: Dict[str, Any]) -> bool:
    """
    Evaluates a declarative rule or composite rule against a facts dictionary.
    Supports:
      - None / {} -> True (no restrictions)
      - {"all": [rule1, rule2, ...]} -> logical AND
      - {"any": [rule1, rule2, ...]} -> logical OR
      - {"not": rule} -> logical NOT
      - Leaf rule: {"field": "...", "operator": "...", "value": "..."}
    """
    if not rule or not isinstance(rule, dict):
        return True

    if "all" in rule:
        sub_rules = rule["all"]
        if not sub_rules:
            return True
        return all(evaluate_condition(sub, facts) for sub in sub_rules)

    if "any" in rule:
        sub_rules = rule["any"]
        if not sub_rules:
            return True
        return any(evaluate_condition(sub, facts) for sub in sub_rules)

    if "not" in rule:
        return not evaluate_condition(rule["not"], facts)

    return evaluate_single_rule(rule, facts)
