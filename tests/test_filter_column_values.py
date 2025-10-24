import pytest
from src.PyDAX import DAXExpression, DAXReference

def test_filter_column_values_rule():
    dax = "FILTER(factSales, factSales[Amount] > 100)"
    expr = DAXExpression(dax)
    assert expr.filter_column_values is not None
    assert expr.filter_column_values.violated is True
    assert len(expr.filter_column_values.violators_tokens) == 1
    
    assert expr.table_column_references == [DAXReference(table_name="factSales", artifact_name="Amount")]
    
def test_no_filter_column_values_rule():
    dax = "CALCULATE(SUM(factSales[Amount]), ALL(factSales))"
    expr = DAXExpression(dax)

    assert expr.filter_column_values is not None
    assert expr.filter_column_values.violated is False
    assert len(expr.filter_column_values.violators_tokens) == 0
    
    assert expr.table_column_references == [DAXReference(table_name="factSales", artifact_name="Amount")]
    
def test_multiple_filter_column_values_rule():
    dax = "FILTER(factSales, factSales[Amount] > 100) + FILTER(factSales, factSales[Quantity] < 50)"
    expr = DAXExpression(dax)

    assert expr.filter_column_values is not None
    assert expr.filter_column_values.violated is True
    assert len(expr.filter_column_values.violators_tokens) == 2
    
    assert expr.table_column_references == [
        DAXReference(table_name="factSales", artifact_name="Amount"),
        DAXReference(table_name="factSales", artifact_name="Quantity"),
    ]