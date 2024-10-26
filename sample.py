from PyDAX import DAXExpression

if __name__ == '__main__':
    # Define a complex DAX expression
    dax_expression = """
    // Calculate average sales per customer, considering only active customers
    VAR SalesPerCustomer = 
        DIVIDE(
            SUM(Sales[TotalAmount]), 
            COUNTROWS(VALUES(Customers[CustomerID]))
        )
        
    // Calculate discount impact
    VAR DiscountImpact = 
        SUMX(
            FILTER(
                Sales,
                Sales[Discount] > 0
            ),
            Sales[DiscountAmount]
        )

    RETURN 
        IF(
            SalesPerCustomer > 500 && DiscountImpact < 1000,
            "High Value Customer",
            "Standard Customer"
        )
    """
    
    # Initialize the DAXExpression object
    expression = DAXExpression(dax_expression)
    
    # Access various properties
    print("Original Expression:", expression.dax_expression)
    print("Expression without Comments:", expression.dax_expression_no_comments)
    print("Table and Column References:", expression.table_column_references)
    print("Extracted Comments:", expression.comments)
    print("Cleaned Expression:", expression.clean_dax_expression)
    print("Contains Division Operator:", expression.contains_div)