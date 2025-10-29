from src.PyDAX import DAXExpression
import pickle

if __name__ == '__main__':
    # Intentionally problematic DAX (for demo purposes):
    # Two unused variables
    # FILTER on table+column inside CALCULATE
    # FILTER on table with measure predicate inside CALCULATE
    dax_expression = """
    // Demo measure with intentional violations
    VAR UnusedVar1 = 123
    VAR SalesPerCustomer = SUM(Sales[Amount]) / COUNTROWS(VALUES(Customers[CustomerID]))
    VAR UnusedVar2 = IFERROR(SUM('Sales'[DiscountAmount]), 0)
    RETURN
    CALCULATE(
        [Total Sales],
        FILTER('Sales', 'Sales'[Quantity] > 10), // column filter (violation)
        FILTER('Sales', [Total Sales] > 1000) // table + measure filter (violation)
    )
    """

    # Initialize the analyzer
    expression = DAXExpression(dax_expression)

    #Comments and comment-free expression
    print("Comments:", expression.comments)
    print("Expression without comments:", expression.dax_expression_no_comments)

    #Table/Column/Measure references
    print("Table/Artifact references:")
    for ref in expression.table_column_references:
        # DAXReference(table_name: str, artifact_name: str)
        print(f" - Table='{ref.table_name}' Artifact='{ref.artifact_name}'")

    #Best practices
    expression.print_best_practices_violations()
    print("Total best-practice violations:", expression.number_of_violations)

    # HTML highlighting (optional)
    # html_code = expression.generate_html_with_violations(name="Demo")
    # expression.save_html_with_violations_to_file("demo_violations.html", name="Demo")


