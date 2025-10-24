import pytest
from src.PyDAX import DAXExpression, DAXReference

def test_avoid_one_minus_division_rule():
    dax = "1 - (Sales[Amount] / Sales[Total])"
    expr = DAXExpression(dax)
    assert expr.avoid_using_1_x_y_syntax is not None
    assert expr.avoid_using_1_x_y_syntax.violated is True
    assert len(expr.avoid_using_1_x_y_syntax.violators_tokens) == 1
    
    assert expr.table_column_references == [
        DAXReference(table_name="Sales", artifact_name="Amount"),
        DAXReference(table_name="Sales", artifact_name="Total"),
    ]
    
def test_no_avoid_one_minus_division_rule():
    dax = "DIVIDE(Sales[Amount], Sales[Total])"
    expr = DAXExpression(dax)

    assert expr.avoid_using_1_x_y_syntax is not None
    assert expr.avoid_using_1_x_y_syntax.violated is False
    assert len(expr.avoid_using_1_x_y_syntax.violators_tokens) == 0
    
    assert expr.table_column_references == [
        DAXReference(table_name="Sales", artifact_name="Amount"),
        DAXReference(table_name="Sales", artifact_name="Total"),
    ]
    
def test_multiple_avoid_one_minus_division_rule():
    dax = "1 - (Sales[Amount] / Sales[Total]) + 1 + (Profit[Value] / Profit[Total])"
    expr = DAXExpression(dax)

    assert expr.avoid_using_1_x_y_syntax is not None
    assert expr.avoid_using_1_x_y_syntax.violated is True
    assert len(expr.avoid_using_1_x_y_syntax.violators_tokens) == 2
    
    assert expr.table_column_references == [
        DAXReference(table_name="Sales", artifact_name="Amount"),
        DAXReference(table_name="Sales", artifact_name="Total"),
        DAXReference(table_name="Profit", artifact_name="Value"),
        DAXReference(table_name="Profit", artifact_name="Total"),
    ]
    
def test_avoid_one_minus_division_in_variable():
    dax = "VAR x = 1 - (Sales[Amount] / Sales[Total]) RETURN x"
    expr = DAXExpression(dax)

    assert expr.avoid_using_1_x_y_syntax is not None
    assert expr.avoid_using_1_x_y_syntax.violated is True
    assert len(expr.avoid_using_1_x_y_syntax.violators_tokens) == 1
    
    assert expr.table_column_references == [
        DAXReference(table_name="Sales", artifact_name="Amount"),
        DAXReference(table_name="Sales", artifact_name="Total"),
    ]
    
def test_avoid_one_plus_division_rule():
    dax = "1 + (Sales[Amount] / Sales[Total])"
    expr = DAXExpression(dax)
    assert expr.avoid_using_1_x_y_syntax is not None
    assert expr.avoid_using_1_x_y_syntax.violated is True
    assert len(expr.avoid_using_1_x_y_syntax.violators_tokens) == 1

    assert expr.table_column_references == [
        DAXReference(table_name="Sales", artifact_name="Amount"),
        DAXReference(table_name="Sales", artifact_name="Total"),
    ]
