from src.PyDAX import DAXExpression
import pickle

if __name__ == '__main__':
    # Intentionally problematic DAX (for demo purposes):
    # Two unused variables
    # FILTER on table+column inside CALCULATE
    # FILTER on table with measure predicate inside CALCULATE
    dax_expression = """
    UDF_model_extension_dependencies()
    """

    # Initialize the analyzer
    expression = DAXExpression(dax_expression)

    # for variable in expression.variables:
    #     print(f"Variable: {variable.name}")
        
    for table_ref in expression.table_references:
        print(f"Table Reference: {table_ref.name}")
    
    for function_ref in expression.function_references:
        print(f"Function Reference: {function_ref.name}")


