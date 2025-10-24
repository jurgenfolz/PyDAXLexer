import pytest
from src.PyDAX import DAXExpression, DAXReference


def test_filter_measure_values_by_column_rule():
    dax = "CALCULATE(SUM(factSales[Amount]), FILTER(ALL(factSales[Category]), factSales[Category] = \"Electronics\"))"
    expr = DAXExpression(dax)
    assert expr.filter_measure_values_by_columns is not None
    assert expr.filter_measure_values_by_columns.violated is True
    assert len(expr.filter_measure_values_by_columns.violators_tokens) == 1
    
    assert expr.table_column_references == [
        DAXReference(table_name="factSales", artifact_name="Amount"),
        DAXReference(table_name="factSales", artifact_name="Category"),
        DAXReference(table_name="factSales", artifact_name="Category"),
    ]
    
def test_no_filter_measure_values_by_column_rule():
    dax = "CALCULATE(SUM(factSales[Amount]), ALL(factSales))"
    expr = DAXExpression(dax)

    assert expr.filter_measure_values_by_columns is not None
    assert expr.filter_measure_values_by_columns.violated is False
    assert len(expr.filter_measure_values_by_columns.violators_tokens) == 0
    
    assert expr.table_column_references == [
        DAXReference(table_name="factSales", artifact_name="Amount"),
    ]
    
def test_multiple_filter_measure_values_by_column_rule():
    dax = "CALCULATE(SUM(factSales[Amount]), FILTER(ALL(factSales[Category]), factSales[Category] = \"Electronics\")) + CALCULATE(SUM(factSales[Amount]), FILTER(ALL(factSales[Region]), factSales[Region] = \"West\"))"
    expr = DAXExpression(dax)

    assert expr.filter_measure_values_by_columns is not None
    assert expr.filter_measure_values_by_columns.violated is True
    assert len(expr.filter_measure_values_by_columns.violators_tokens) == 2
    
    assert expr.table_column_references == [
        DAXReference(table_name="factSales", artifact_name="Amount"),
        DAXReference(table_name="factSales", artifact_name="Category"),
        DAXReference(table_name="factSales", artifact_name="Category"),
        DAXReference(table_name="factSales", artifact_name="Amount"),
        DAXReference(table_name="factSales", artifact_name="Region"),
        DAXReference(table_name="factSales", artifact_name="Region"),
    ]