import pytest
from src.PyDAX import DAXExpression, DAXReference

def test_evaluatelog_rule():
    dax = "EVALUATEANDLOG([Actual Temperature (℃)])"
    expr = DAXExpression(dax)
    
    assert expr.evaluateandlog_should_not_be_used_in_production_models is not None
    assert expr.evaluateandlog_should_not_be_used_in_production_models.violated is True
    assert len(expr.evaluateandlog_should_not_be_used_in_production_models.violators_tokens) == 1
    
    assert expr.table_column_references == [DAXReference(table_name="", artifact_name="Actual Temperature (℃)")]
    
def test_no_evaluatelog_rule():
    dax = "SUM(factWeather[temp_c])"
    expr = DAXExpression(dax)

    assert expr.evaluateandlog_should_not_be_used_in_production_models is not None
    assert expr.evaluateandlog_should_not_be_used_in_production_models.violated is False
    assert len(expr.evaluateandlog_should_not_be_used_in_production_models.violators_tokens) == 0
    
    assert expr.table_column_references == [DAXReference(table_name="factWeather", artifact_name="temp_c")]
    
    
def test_multiple_evaluatelog_rule():
    dax = "EVALUATEANDLOG([Measure1]) + EVALUATEANDLOG([Measure2])"
    expr = DAXExpression(dax)

    assert expr.evaluateandlog_should_not_be_used_in_production_models is not None
    assert expr.evaluateandlog_should_not_be_used_in_production_models.violated is True
    assert len(expr.evaluateandlog_should_not_be_used_in_production_models.violators_tokens) == 2
    
    assert expr.table_column_references == [
        DAXReference(table_name="", artifact_name="Measure1"),
        DAXReference(table_name="", artifact_name="Measure2"),
    ]