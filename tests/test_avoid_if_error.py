import pytest
from src.PyDAX import DAXExpression

def test_avoid_iferror_rule():
    dax = "IFERROR(1/0, 0)"
    expr = DAXExpression(dax)
    assert expr.avoid_using_iferror_function is not None
    assert expr.avoid_using_iferror_function.violated is True
    assert len(expr.avoid_using_iferror_function.violators_tokens) == 1
    
    assert expr.table_column_references == []
    

def test_no_iferror_rule():
    dax = "DIVIDE(1, 0)"
    expr = DAXExpression(dax)

    assert expr.avoid_using_iferror_function is not None
    assert expr.avoid_using_iferror_function.violated is False
    assert len(expr.avoid_using_iferror_function.violators_tokens) == 0
    
    assert expr.table_column_references == []
    
def test_multiple_iferror_rule():
    dax = "IFERROR(1/0, 0) + IFERROR(2/0, 0)"
    expr = DAXExpression(dax)

    assert expr.avoid_using_iferror_function is not None
    assert expr.avoid_using_iferror_function.violated is True
    assert len(expr.avoid_using_iferror_function.violators_tokens) == 2
    
    assert expr.table_column_references == []
    
def test_iferror_in_variable():
    dax = "VAR x = IFERROR(1/0, 0) RETURN x"
    expr = DAXExpression(dax)

    assert expr.avoid_using_iferror_function is not None
    assert expr.avoid_using_iferror_function.violated is True
    assert len(expr.avoid_using_iferror_function.violators_tokens) == 1
    
    assert expr.table_column_references == []
    
    