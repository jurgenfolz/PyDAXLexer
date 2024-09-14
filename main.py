from src.PyDAX import DAXExpression


if __name__ == '__main__':
    
    dax_expression = """
        // Comment here
        EVALUATE
        CALCULATETABLE (
            ADDCOLUMNS (
                Sales,
                "PreviousMonthSales", CALCULATE (
                    [Total Sales],
                    PREVIOUSMONTH ( 'Date'[Date_col] )
                )
            )
        )
        /* Lines 
        of 
        comments */
        """
    
    processor = DAXExpression(dax_expression)
    comments = processor.extract_comments()
    print(comments)
    
    dax_without_comments = processor.remove_comments()
    print(dax_without_comments)
    
    columns_measures = processor.extract_columns_measures()
    for column_measure in columns_measures:
        print(column_measure)
        
    table_column_references = processor.extract_table_column_references()
    for table_column_reference in table_column_references:
        print(table_column_reference)