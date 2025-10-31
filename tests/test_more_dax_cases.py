import pytest

from src.PyDAX import (
    DAXExpression,
    DAXArtifactReference,
    DAXTableReference,
    DAXVariableReference,
    DAXFunctionReference,
)


def test_var_shadowing_table_name(make_artifact_ref, make_variable_ref):
    dax = (
        "VAR Sales = SUM(Sales[Amount])\n"
        "RETURN Sales"
    )
    expr = DAXExpression(dax)

    # Variable declaration captured
    assert [v.name for v in expr.variables] == ["Sales"]

    # Column reference still captured with table 'Sales'
    assert make_artifact_ref(table_name="Sales", artifact_name="Amount") in expr.table_column_references

    # Variable reference captured for RETURN Sales
    assert make_variable_ref(name="Sales") in expr.variable_references


def test_udf_nested_calls(make_function_ref):
    dax = "OuterUDF(InnerUDF(1))"
    expr = DAXExpression(dax)

    # Both UDFs detected as function references
    assert make_function_ref(name="OuterUDF") in expr.function_references
    assert make_function_ref(name="InnerUDF") in expr.function_references


def test_standalone_quoted_table_references(make_artifact_ref, make_table_ref):
    dax = (
        "CALCULATE(\n"
        "    SUM('Dim Date'[Year]),\n"
        "    FILTER('Dim Date', 'Dim Date'[Year] > 2020),\n"
        "    VALUES('Dim Date')\n"
        ")"
    )
    expr = DAXExpression(dax)

    # Column references captured
    assert make_artifact_ref(table_name="Dim Date", artifact_name="Year") in expr.table_column_references

    # Standalone table reference captured (quotes stripped in reference)
    assert make_table_ref(name="Dim Date") in expr.table_references


def test_calculatetable_with_treatas_and_udf(make_artifact_ref, make_function_ref):
    dax = (
        "CALCULATETABLE(\n"
        "    VALUES(DimCustomer[CustomerKey]),\n"
        "    TREATAS(MyUDFTable(), DimCustomer[CustomerKey])\n"
        ")"
    )
    expr = DAXExpression(dax)

    # Column references present
    assert make_artifact_ref(table_name="DimCustomer", artifact_name="CustomerKey") in expr.table_column_references

    # UDF used in table context is detected as function reference
    assert make_function_ref(name="MyUDFTable") in expr.function_references


def test_variables_complex_math_and_functions(make_artifact_ref):
    dax = (
        "VAR a = SUMX(VALUES(DimProduct[Category]), [Measure])\n"
        "VAR b = DIVIDE(a, COUNTROWS(DimProduct))\n"
        "RETURN a + b"
    )
    expr = DAXExpression(dax)

    # Two variables a and b
    assert {v.name for v in expr.variables} == {"a", "b"}

    # Variable references in RETURN a + b and inside DIVIDE(a, ...)
    var_names = {v.name for v in expr.variable_references}
    assert {"a", "b"}.issubset(var_names)

    # Column references include table DimProduct and measure [Measure]
    assert make_artifact_ref(table_name="DimProduct", artifact_name="Category") in expr.table_column_references
    assert make_artifact_ref(table_name="", artifact_name="Measure") in expr.table_column_references


def test_udf_table_argument_in_iteration(make_function_ref, make_artifact_ref):
    dax = "SUMX(MyTableUDF(), [Value])"
    expr = DAXExpression(dax)

    # UDF used as table input for SUMX
    assert make_function_ref(name="MyTableUDF") in expr.function_references
    # Measure/column reference [Value] captured as standalone artifact
    assert make_artifact_ref(table_name="", artifact_name="Value") in expr.table_column_references
