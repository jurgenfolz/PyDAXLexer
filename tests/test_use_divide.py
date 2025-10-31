import pytest
from src.PyDAX import DAXExpression, DAXArtifactReference

def test_use_divide_rule():
    dax = "1 / 0"
    expr = DAXExpression(dax)
    assert expr.use_divide_function_for_division is not None
    assert expr.use_divide_function_for_division.violated is True
    assert len(expr.use_divide_function_for_division.violators_tokens) == 1
    
    assert expr.table_column_references == []
    
def test_no_use_divide_rule():
    dax = "DIVIDE(1, 0)"
    expr = DAXExpression(dax)

    assert expr.use_divide_function_for_division is not None
    assert expr.use_divide_function_for_division.violated is False
    assert len(expr.use_divide_function_for_division.violators_tokens) == 0
    
    assert expr.table_column_references == []
    
def test_multiple_use_divide_rule():
    dax = "1 / 0 + 2 / 0"
    expr = DAXExpression(dax)

    assert expr.use_divide_function_for_division is not None
    assert expr.use_divide_function_for_division.violated is True
    assert len(expr.use_divide_function_for_division.violators_tokens) == 2
    
    assert expr.table_column_references == []
    
def test_use_divide_in_variable():
    dax = "VAR x = 1 / 0 RETURN x"
    expr = DAXExpression(dax)

    assert expr.use_divide_function_for_division is not None
    assert expr.use_divide_function_for_division.violated is True
    assert len(expr.use_divide_function_for_division.violators_tokens) == 1
    
    assert expr.table_column_references == []
    
def test_use_divide_with_columns(make_artifact_ref):
    dax = "DIVIDE(Sales[Amount], Sales[Total])"
    expr = DAXExpression(dax)

    assert expr.use_divide_function_for_division is not None
    assert expr.use_divide_function_for_division.violated is False
    assert len(expr.use_divide_function_for_division.violators_tokens) == 0
    
    assert expr.table_column_references == [
        make_artifact_ref(table_name="Sales", artifact_name="Amount"),
        make_artifact_ref(table_name="Sales", artifact_name="Total"),
    ]
    
def test_use_divide_with_mixed(make_artifact_ref):
    dax = "1 / 0 + DIVIDE(Sales[Amount], Sales[Total])"
    expr = DAXExpression(dax)

    assert expr.use_divide_function_for_division is not None
    assert expr.use_divide_function_for_division.violated is True
    assert len(expr.use_divide_function_for_division.violators_tokens) == 1
    
    assert expr.table_column_references == [
        make_artifact_ref(table_name="Sales", artifact_name="Amount"),
        make_artifact_ref(table_name="Sales", artifact_name="Total"),
    ]