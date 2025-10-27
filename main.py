from src.PyDAX import DAXExpression

if __name__ == '__main__':

    
    dax_expression =  "CALCULATE([Total Sales], FILTER('Sales', 'Sales'[Quantity] > 10))"

    expression = DAXExpression(dax_expression)
    expression.print_best_practices_violations()
    print(expression.number_of_violations)
    
    
    