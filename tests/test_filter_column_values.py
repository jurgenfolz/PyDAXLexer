import pytest
from src.PyDAX import DAXExpression

#! DAX expression that violates the rule
dax_violates = "CALCULATE([Total Sales], FILTER('Sales', 'Sales'[Quantity] > 10))"

#* DAX expression that does not violate the rule (using FILTER on a measure result, not a simple column filter)
dax_does_not_violate = "CALCULATE([Total Sales], FILTER(VALUES('Date'[Year]), [Sales Amount] > 100000))"

#! DAX expression that violates the rule multiple times
dax_violates_multiple = "CALCULATE([Total Sales], FILTER('Sales', 'Sales'[Quantity] > 10), FILTER('Product', 'Product'[Color] = \"Red\"))"

#? DAX with standalone FILTER (should not violate) with CALCULATE and CALCULATETABLE commented out
#* This should not trigger a violation as FILTER is not used within CALCULATE/CALCULATETABLE
dax_standalone_filter = """//CALCULATE( CALCULATETABLE(
FILTER('Sales', 'Sales'[Quantity] > 10)"""

def test_single_violation():
    """Tests that the rule is violated when CALCULATE contains a simple FILTER on a column."""
    expr = DAXExpression(dax_violates)
    
    assert expr.filter_column_values.violated, "The rule should be marked as violated."
    assert len(expr.filter_column_values.violators_tokens) == 1, "There should be exactly one violating token."
    assert expr.filter_column_values.violators_tokens[0].text.upper() == "FILTER", "The violating token should be 'FILTER'."

def test_no_violation_with_complex_filter():
    """Tests that the rule is not violated when FILTER is used on a measure or a more complex expression."""
    expr = DAXExpression(dax_does_not_violate)

    assert not expr.filter_column_values.violated, "The rule should not be marked as violated for complex FILTER scenarios."
    assert len(expr.filter_column_values.violators_tokens) == 0, "There should be no violating tokens."


#! Limitation: Currently n ot checking for multiple violations on the same expression
# def test_multiple_violations():
#     """Tests that the rule correctly identifies multiple violations in the same expression."""
#     expr = DAXExpression(dax_violates_multiple)

#     assert expr.filter_column_values.violated, "The rule should be marked as violated."
#     assert len(expr.filter_column_values.violators_tokens) == 2, "There should be two violating tokens."
#     for token in expr.filter_column_values.violators_tokens:
#         assert token.text.upper() == "FILTER", "Each violating token should be 'FILTER'."

def test_no_violation_with_keepfilters():
    """Tests that using KEEPFILTERS instead of FILTER does not trigger a violation."""
    dax_with_keepfilters = "CALCULATE([Total Sales], KEEPFILTERS('Sales'[Quantity] > 10))"
    expr = DAXExpression(dax_with_keepfilters)

    assert not expr.filter_column_values.violated, "Using KEEPFILTERS should not trigger a violation."
    assert len(expr.filter_column_values.violators_tokens) == 0, "There should be no violating tokens with KEEPFILTERS."

def test_no_violation_standalone_filter():
    """Tests that a standalone FILTER function call does not trigger a violation."""
    expr = DAXExpression(dax_standalone_filter)

    assert not expr.filter_column_values.violated, "A standalone FILTER should not trigger a violation."
    assert len(expr.filter_column_values.violators_tokens) == 0, "There should be no violating tokens for a standalone FILTER."
    