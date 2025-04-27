from src.PyDAX import DAXExpression

if __name__ == '__main__':
    
    dax_expression = """
    Total Bike Sales 1 =

        VAR TotalSales =

            SUMX (

                'VF Cycles Sales',

                'VF Cycles Sales'[Quantity_Sold] * RELATED ( 'VF Cycles Products'[Unit Price] )

            )

        VAR BikeSales =

            CALCULATE (

                TotalSales,

                KEEPFILTERS ( 'VF Cycles Products'[Product Category] = "Bikes" )

            )

        RETURN

            BikeSales
    
        """
    
    expression = DAXExpression(dax_expression)
    print(expression.dax_expression)
    print(expression.dax_expression_no_comments)
    print(expression.table_column_references)
    print(expression.comments)
    print(expression.clean_dax_expression)
    
    print(expression.contains_div)
    