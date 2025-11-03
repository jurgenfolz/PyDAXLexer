from src.PyDAX import DAXExpression


def test_generate_html_includes_string_quotes():
    dax = (
        "SWITCH(\n"
        "    [Selected metric],\n"
        "    \"Temperature\", [Average Temperature (℃)],\n"
        "    \"Condition\", 1\n"
        ")"
    )
    expr = DAXExpression(dax)
    html = expr.generate_html()
    assert '"Temperature"' in html
    assert '"Condition"' in html


def test_generate_html_with_violations_includes_string_quotes():
    dax = (
        "SWITCH(\n"
        "    [Selected metric],\n"
        "    \"Temperature\", [Average Temperature (℃)],\n"
        "    \"Condition\", 1\n"
        ")"
    )
    expr = DAXExpression(dax)
    html = expr.generate_html_with_violations()
    assert '"Temperature"' in html
    assert '"Condition"' in html
