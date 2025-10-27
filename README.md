# PyDAX

`PyDAX` is a package designed to analyze DAX expressions. It can extract comments, remove comments, and identify columns and measures referenced in DAX expressions.


## Installation

To install the package, use pip:

```bash
pip install PyDAXLexer
```
## Usage

Here's how to use `PyDAXLexer` to analyze a DAX expression and surface helpful insights.

The example below intentionally violates a few best-practice rules (notably Unused Variables and FILTER patterns), and demonstrates how to:
- Extract comments and remove comments
- Extract table/column/measure references
- Verify best practices and list violating tokens
- Generate HTML highlighting violations

```python
from PyDAX import DAXExpression

if __name__ == '__main__':
    # Intentionally problematic DAX (for demo purposes):
    # Two unused variables
    # FILTER on table+column inside CALCULATE
    # FILTER on table with measure predicate inside CALCULATE
    dax_expression = """
    // Demo calc with intentional violations
    VAR UnusedVar1 = 123
    VAR SalesPerCustomer = SUM(Sales[Amount]) / COUNTROWS(VALUES(Customers[CustomerID]))
    VAR UnusedVar2 = IFERROR(SUM('Sales'[DiscountAmount]), 0)
    RETURN
    CALCULATE(
        [Total Sales],
        FILTER('Sales', 'Sales'[Quantity] > 10),            // column filter (violation)
        FILTER('Sales', [Total Sales] > 1000)               // table + measure filter (violation)
    )
    """

    # Initialize the analyzer
    expression = DAXExpression(dax_expression)

    #Comments and comment-free expression
    print("Comments:", expression.comments)
    print("Expression without comments:", expression.dax_expression_no_comments)

    #Table/Column/Measure references
    print("Table/Artifact references:")
    for ref in expression.table_column_references:
        # DAXReference(table_name: str, artifact_name: str)
        print(f" - Table='{ref.table_name}' Artifact='{ref.artifact_name}'")

    #Best practices
    expression.print_best_practices_violations()
    print("Total best-practice violations:", expression.number_of_violations)

    # HTML highlighting (optional)
    # html_code = expression.generate_html_with_violations(name="Demo")
    # expression.save_html_with_violations_to_file("demo_violations.html", name="Demo")
```

## Additional Features

The DAXExpression class provides several utility methods:

- `remove_comments()`: Returns the expression with comments removed (accessible as `dax_expression_no_comments`).
- `extract_comments()`: Returns a list of comment strings (accessible as `comments`).
- `extract_artifact_references()`: Returns table/column/measure references as `DAXReference` objects (accessible as `table_column_references`).
- `generate_html(light: bool)`: Generates HTML output with syntax coloring.
- `generate_html_with_violations(name: str, light: bool)`: Generates HTML and highlights best-practice violations.
- `save_html_to_file(file_name: str)`: Saves the syntax-colored HTML output to a file.
- `save_html_with_violations_to_file(file_name: str)`: Saves the violations-highlighted HTML output to a file.

### Best-practices overview

When `DAXExpression` is created, it initializes a set of best-practice rules and verifies them by default. You can access:

- `best_practice_rules`: List of rule instances
- `number_of_violations`: Total count of violations across all rules
- `print_best_practices_violations()`: Print rule names and violating tokens with locations

Included rules (subject to change):
- Use DIVIDE instead of division operator
- Avoid IFERROR
- Use TREATAS instead of INTERSECT
- Filter column values with proper syntax
- Filter measure values by columns, not tables
- Unused variables
- Avoid 1 - x/y syntax
- Avoid EvaluateAndLog in production

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


