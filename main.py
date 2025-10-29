from src.PyDAX import DAXExpression

if __name__ == '__main__':
    # Same example as documented in README.md
    dax_expression = """
    VAR UnusedVar1 = UDF_testFunction()
    RETURN
    CALCULATE(
        [Total Sales]
    )
    """

    expression = DAXExpression(dax_expression)
    expression.print_tokens()
    # Comments and comment-free expression
    # print("Comments:", expression.comments)
    # print("Expression without comments:", expression.dax_expression_no_comments)

    # # Table/Artifact references
    # print("Table/Artifact references:")
    # for ref in expression.table_column_references:
    #     print(f" - Table='{ref.table_name}' Artifact='{ref.artifact_name}'")

    # # Best practices
    # expression.print_best_practices_violations()
    # print("Total best-practice violations:", expression.number_of_violations)

    # # Optional: save HTML with violations highlighted
    # # expression.save_html_with_violations_to_file("demo_violations.html", name="Demo")


