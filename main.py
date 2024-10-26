from src.PyDAX import DAXExpression

if __name__ == '__main__':
    
    dax_expression = """"Chance of Snow (%) in "&SELECTEDVALUE(dCities[name])
        """
    
    expression = DAXExpression(dax_expression)
    print(expression.dax_expression)
    print(expression.dax_expression_no_comments)
    print(expression.table_column_references)
    print(expression.comments)
    print(expression.clean_dax_expression)
    
    print(expression.contains_div)
    