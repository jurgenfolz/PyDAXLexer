import pytest
from src.PyDAX import DAXExpression


def _extract_first(expr: DAXExpression):
    assert len(expr.relationship_references) >= 1, "Expected at least one USERELATIONSHIP reference"
    return expr.relationship_references[0]


def test_simple_userelationship_reference():
    dax = "CALCULATE(COUNTROWS(trCountries), USERELATIONSHIP(dimCountries[country_code], trCountries[Country]))"
    expr = DAXExpression(dax)

    assert len(expr.relationship_references) == 1
    rel = _extract_first(expr)
    assert rel.table1 == "dimCountries"
    assert rel.column1 == "country_code"
    assert rel.table2 == "trCountries"
    assert rel.column2 == "Country"
    # String display
    assert str(rel) == "dimCountries[country_code] -> trCountries[Country]"


def test_userelationship_reverse_order():
    dax = "USERELATIONSHIP(trCountries[Country], dimCountries[country_code])"
    expr = DAXExpression(dax)

    assert len(expr.relationship_references) == 1
    rel = _extract_first(expr)
    assert rel.table1 == "trCountries"
    assert rel.column1 == "Country"
    assert rel.table2 == "dimCountries"
    assert rel.column2 == "country_code"


def test_userelationship_with_comment():
    dax = "USERELATIONSHIP(trCountries[Country],/*comment here*/ dimCountries[country_code])"
    expr = DAXExpression(dax)

    assert len(expr.relationship_references) == 1
    rel = _extract_first(expr)
    assert rel.table1 == "trCountries"
    assert rel.column1 == "Country"
    assert rel.table2 == "dimCountries"
    assert rel.column2 == "country_code"

def test_multiple_userelationships():
    dax = (
        "CALCULATE("
        " [Some Measure],"
        " USERELATIONSHIP('Dim Date'[Date], 'Fact Sales'[Date]),"
        " USERELATIONSHIP(Inventory[ProductId], 'Dim Product'[ProductId])"
        ")"
    )
    expr = DAXExpression(dax)

    assert len(expr.relationship_references) == 2
    a, b = expr.relationship_references
    assert (a.table1, a.column1, a.table2, a.column2) == ("Dim Date", "Date", "Fact Sales", "Date") or \
           (b.table1, b.column1, b.table2, b.column2) == ("Dim Date", "Date", "Fact Sales", "Date")
    assert (a.table1, a.column1, a.table2, a.column2) == ("Inventory", "ProductId", "Dim Product", "ProductId") or \
           (b.table1, b.column1, b.table2, b.column2) == ("Inventory", "ProductId", "Dim Product", "ProductId")


def test_userelationship_inside_complex_expression():
    dax = (
        "VAR x = CALCULATE("
        "    [Total Sales],"
        "    USERELATIONSHIP('Dim Date'[Date], 'Fact Sales'[OrderDate]),"
        "    FILTER('Fact Sales', 'Fact Sales'[Amount] > 0)"
        ") RETURN x"
    )
    expr = DAXExpression(dax)

    assert len(expr.relationship_references) == 1
    rel = _extract_first(expr)
    assert rel.table1 == "Dim Date"
    assert rel.column1 == "Date"
    assert rel.table2 == "Fact Sales"
    assert rel.column2 == "OrderDate"
