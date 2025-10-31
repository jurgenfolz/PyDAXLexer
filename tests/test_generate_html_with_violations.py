from src.PyDAX import DAXExpression


def test_generate_html_highlights_division_operator():
    expr = DAXExpression("1 / 0")
    html = expr.generate_html_with_violations(light=True)
    # Expect wavy underline styling indicating a violation highlight
    assert "text-decoration-style: wavy" in html
    assert "#ff0000" in html  # red text for violations


def test_generate_html_no_highlight_when_using_divide():
    expr = DAXExpression("DIVIDE(1, 0)")
    html = expr.generate_html_with_violations(light=True)
    # No violation should be highlighted for proper DIVIDE usage
    assert "text-decoration-style: wavy" not in html
