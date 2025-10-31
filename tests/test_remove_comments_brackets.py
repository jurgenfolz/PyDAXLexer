import pytest
from src.PyDAX import DAXExpression


def test_remove_comments_preserves_brackets():
    expr_text = "CALCULATE(COUNTROWS(trCountries),USERELATIONSHIP(dimCountries[country_code],trCountries[Country]))"
    expr = DAXExpression(expr_text)
    no_comments = expr.remove_comments()
    assert no_comments == expr_text


def test_remove_comments_with_comments_and_brackets():
    expr_text = "// lead comment\nCALCULATE(/* mid */COUNTROWS(trCountries),USERELATIONSHIP(dimCountries[country_code],trCountries[Country]))// tail"
    expected = "\nCALCULATE(COUNTROWS(trCountries),USERELATIONSHIP(dimCountries[country_code],trCountries[Country]))"
    expr = DAXExpression(expr_text)
    no_comments = expr.remove_comments()
    assert no_comments == expected
