from src.PyDAX import DAXExpression

if __name__ == '__main__':

    with open(r'resources\best_practices_violators\unused_variables_mixed_3_used_3_unused.txt', 'r', encoding='utf-8') as f:
        dax_expression = f.read()

    expression = DAXExpression(dax_expression)
    expression.print_best_practices_violations()
    print(expression.number_of_violations)
    
    
    