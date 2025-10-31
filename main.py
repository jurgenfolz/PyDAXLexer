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
    VAR UnusedVar2 = UDF_test_abc()
    RETURN
    CALCULATE(
        [Total Sales],
    )
    """

    # Initialize the analyzer
    expression = DAXExpression(dax_expression)

    #Comments and comment-free expression
    expression.print_tokens()
    


