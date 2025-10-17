from src.PyDAX import DAXExpression

if __name__ == '__main__':
    
    dax_expression = """
    () => max(factWeather[temp_c]) + max(factWeather[chance_of_snow])
    
        """
    
    expression = DAXExpression(dax_expression)
    expression.print_tokens()
    print(expression.table_column_references)