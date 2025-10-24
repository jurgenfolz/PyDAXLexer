import pytest
from src.PyDAX import DAXExpression, DAXReference

def test_use_treatas_instead_of_intersect_rule():
    dax = "INTERSECT(Table1, Table2)"
    expr = DAXExpression(dax)
    assert expr.use_the_treatas_function_instead_of_intersect is not None
    assert expr.use_the_treatas_function_instead_of_intersect.violated is True
    assert len(expr.use_the_treatas_function_instead_of_intersect.violators_tokens) == 1
    
    assert expr.table_column_references == []
    
def test_no_use_treatas_instead_of_intersect_rule():
    dax = "TREATAS(Table1, Table2)"
    expr = DAXExpression(dax)

    assert expr.use_the_treatas_function_instead_of_intersect is not None
    assert expr.use_the_treatas_function_instead_of_intersect.violated is False
    assert len(expr.use_the_treatas_function_instead_of_intersect.violators_tokens) == 0
    
    assert expr.table_column_references == []
    
def test_multiple_use_treatas_instead_of_intersect_rule():
    dax = "INTERSECT(Table1, Table2) + INTERSECT(Table3, Table4)"
    expr = DAXExpression(dax)

    assert expr.use_the_treatas_function_instead_of_intersect is not None
    assert expr.use_the_treatas_function_instead_of_intersect.violated is True
    assert len(expr.use_the_treatas_function_instead_of_intersect.violators_tokens) == 2
    
    assert expr.table_column_references == []
    
def test_use_treatas_in_variable():
    dax = "VAR x = INTERSECT(Table1, Table2) RETURN x"
    expr = DAXExpression(dax)

    assert expr.use_the_treatas_function_instead_of_intersect is not None
    assert expr.use_the_treatas_function_instead_of_intersect.violated is True
    assert len(expr.use_the_treatas_function_instead_of_intersect.violators_tokens) == 1
    
    assert expr.table_column_references == []
    
def test_use_treatas_with_columns():
    dax = "TREATAS(Table1[ColumnA], Table2[ColumnB])"
    expr = DAXExpression(dax)

    assert expr.use_the_treatas_function_instead_of_intersect is not None
    assert expr.use_the_treatas_function_instead_of_intersect.violated is False
    assert len(expr.use_the_treatas_function_instead_of_intersect.violators_tokens) == 0
    
    assert expr.table_column_references == [
        DAXReference(table_name="Table1", artifact_name="ColumnA"),
        DAXReference(table_name="Table2", artifact_name="ColumnB"),
    ]