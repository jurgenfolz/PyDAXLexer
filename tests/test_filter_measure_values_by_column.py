import pytest
from src.PyDAX import DAXExpression


#! Violation: using FILTER('Table', [Measure] > value) inside CALCULATE
dax_violates = "CALCULATE([Total Sales], FILTER('Sales', [Total Sales] > 10))"

#* No violation: using FILTER over a specific column with VALUES
dax_no_violation_values = "CALCULATE([Total Sales], FILTER(VALUES('Sales'[Quantity]), [Total Sales] > 10))"

#* No violation: using FILTER over a specific column with ALL
dax_no_violation_all = "CALCULATE([Total Sales], FILTER(ALL('Sales'[Quantity]), [Total Sales] > 10))"

# Multiple violations: two FILTER('Table', [Measure] ...) inside CALCULATE
dax_violates_multiple = (
    "CALCULATE([Total Sales], FILTER('Sales', [Total Sales] > 10), FILTER('Product', [Total Sales] > 5))"
)

#* Standalone FILTER should not violate (no CALCULATE/CALCULATETABLE in default channel)
dax_standalone_filter = "FILTER('Sales', [Total Sales] > 10)"


def test_single_violation():
    expr = DAXExpression(dax_violates)

    assert expr.filter_measure_values_by_columns is not None
    assert expr.filter_measure_values_by_columns.violated is True
    assert len(expr.filter_measure_values_by_columns.violators_tokens) == 1
    assert expr.filter_measure_values_by_columns.violators_tokens[0].text.upper() == "FILTER"


def test_no_violation_with_values_column():
    expr = DAXExpression(dax_no_violation_values)

    assert expr.filter_measure_values_by_columns is not None
    assert expr.filter_measure_values_by_columns.violated is False
    assert len(expr.filter_measure_values_by_columns.violators_tokens) == 0


def test_no_violation_with_all_column():
    expr = DAXExpression(dax_no_violation_all)

    assert expr.filter_measure_values_by_columns is not None
    assert expr.filter_measure_values_by_columns.violated is False
    assert len(expr.filter_measure_values_by_columns.violators_tokens) == 0

#! Limitation: Currently n ot checking for multiple violations on the same expression
# def test_multiple_violations():
#     expr = DAXExpression(dax_violates_multiple)

#     assert expr.filter_measure_values_by_columns is not None
#     assert expr.filter_measure_values_by_columns.violated is True
#     assert len(expr.filter_measure_values_by_columns.violators_tokens) == 2
#     for token in expr.filter_measure_values_by_columns.violators_tokens:
#         assert token.text.upper() == "FILTER"


def test_no_violation_standalone_filter():
    expr = DAXExpression(dax_standalone_filter)

    assert expr.filter_measure_values_by_columns is not None
    assert expr.filter_measure_values_by_columns.violated is False
    assert len(expr.filter_measure_values_by_columns.violators_tokens) == 0