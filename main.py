from src.PyDAX import DAXExpression
import pickle

if __name__ == '__main__':
    # Intentionally problematic DAX (for demo purposes):
    # Two unused variables
    # FILTER on table+column inside CALCULATE
    # FILTER on table with measure predicate inside CALCULATE
    dax_expression = """
    // Sales KPI with tables, functions, variables, and a UDF
    VAR selected_date = SELECTEDVALUE('Date'[Date])
    VAR sales_curr =
        CALCULATE(
            [Total Sales],
            DATESINPERIOD('Date'[Date], selected_date, -1, MONTH),
            FILTER(FactSales, FactSales[SalesAmount] > 0)          // standalone table + table[column]
        )
    var sales_prev =                                         // lowercase var on purpose
        CALCULATE(
            [Total Sales],
            DATESINPERIOD('Date'[Date], selected_date, -2, MONTH),
            REMOVEFILTERS(DimProduct)                         // standalone table
        )
    VAR cust_count = DISTINCTCOUNT(FactSales[CustomerKey])    // table[column]
    VAR cat_tbl = VALUES(DimProduct[Category])                // variable holding a table
    VAR ratio = DIVIDE(sales_curr - sales_prev, cust_count)   // function with variables
    VAR label = IF(ratio > 0.1, "Up", "Down")
    RETURN
    IF(
        NOT ISBLANK(selected_date) && MyUDF(selected_date) >= 0,   // UDF call
        FORMAT(ratio, "#,0.00%") & " " & label & " (" & COUNTROWS(cat_tbl) & ")",
        BLANK()
    )
    """

    # Initialize the analyzer
    expression = DAXExpression(dax_expression)

    # for variable in expression.variables:
    #     print(f"Variable: {variable.name}")
        
    for table_ref in expression.table_references:
        print(f"Table Reference: {table_ref.name}")
    
    for function_ref in expression.function_references:
        print(f"Function Reference: {function_ref.name}")


