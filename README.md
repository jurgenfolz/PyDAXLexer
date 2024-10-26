# PyDAX

`PyDAX` is a package designed to analyze DAX expressions. It can extract comments, remove comments, and identify columns and measures referenced in DAX expressions.


## Installation

To install the package, use pip:

```bash
pip install PyDAXLexer
```
## Usage

Here's a how to use PyDAXLexer. This example shows how to create a DAXExpression object and extract information.

```python
from PyDAX import DAXExpression

if __name__ == '__main__':
    # DAX expression as string:
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
```

## Additional Features

The DAXExpression class provides several utility methods:

- `remove_comments()`: Removes comments from the DAX expression.
- `extract_comments()`: Extracts all comments in the expression.
- `extract_artifact_references()`: Extracts table and column references.
- `generate_html(light: bool)`: Generates HTML output of the expression with syntax coloring.
- `save_html_to_file(file_name: str)`: Saves the syntax-colored HTML output to a file.

## License

This project is licensed under the MIT License.

## Acknowledgments

### TabularEditor

The lexer grammar used in this project is adapted from the TabularEditor GitHub repository.

- **Source**: [TabularEditor GitHub Repository](https://github.com/TabularEditor/TabularEditor/blob/master/AntlrGrammars/DAXLexer.g4)
- **License**: MIT License

### ANTLR

This project uses ANTLR (ANother Tool for Language Recognition) to generate the lexer and parser for DAX expressions. 

- **Project**: The ANTLR Project
- **License**: BSD-3-Clause License


