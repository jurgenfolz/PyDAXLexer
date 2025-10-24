from pathlib import Path

from src.PyDAX import DAXExpression
from src.PyDAX.best_practices_rules import UnusedVariables


def read_violator(name: str) -> str:
    root = Path(__file__).resolve().parents[1]
    p = root / "resources" / "best_practices_violators" / name
    return p.read_text(encoding="utf-8")


def get_unused_rule(expr: DAXExpression) -> UnusedVariables:
    for rule in expr.best_practice_rules:
        if isinstance(rule, UnusedVariables) or getattr(rule, "id", "") == "UNUSED_VARIABLES":
            return rule  # type: ignore[return-value]
    raise AssertionError("UnusedVariables rule not found in best_practice_rules")


def test_unused_variables_mixed_3_used_3_unused():
    dax = read_violator("unused_variables_mixed_3_used_3_unused.txt")
    expr = DAXExpression(dax)
    rule = get_unused_rule(expr)
    assert rule.violated is True
    assert len(rule.violators_tokens) == 3


def test_unused_variables_all_used_3():
    dax = read_violator("unused_variables_all_used_3.txt")
    expr = DAXExpression(dax)
    rule = get_unused_rule(expr)
    assert rule.violated is False
    assert len(rule.violators_tokens) == 0


def test_unused_variables_comment_only():
    dax = read_violator("unused_variables_comment_only.txt")
    expr = DAXExpression(dax)
    rule = get_unused_rule(expr)
    assert rule.violated is True
    assert len(rule.violators_tokens) == 2
