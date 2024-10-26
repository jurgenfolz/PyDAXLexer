import pytest
from antlr4 import InputStream
from src.PyDAX.lexer import PyDAXLexer
from PyDAX.DAXExpression import DAXExpression

@pytest.fixture
def sample_dax():
    return """
    // This is a single line comment
    EVALUATE
    CALCULATETABLE (
        ADDCOLUMNS (
            Sales,
            "PreviousMonthSales", CALCULATE (
                Sales[Total Sales],
                PREVIOUSMONTH ( 'Date'[Date] )
            )
        )
    )
    /* This is a
    multi-line comment */
    """

def test_extract_comments(sample_dax):
    processor = DAXProcessor(sample_dax)
    comments = processor.extract_comments()
    assert comments == ["// This is a single line comment", "/* This is a\n    multi-line comment */"]

def test_remove_comments(sample_dax):
    processor = DAXProcessor(sample_dax)
    dax_without_comments = processor.remove_comments()
    expected_dax = """
    
    EVALUATE
    CALCULATETABLE (
        ADDCOLUMNS (
            Sales,
            "PreviousMonthSales", CALCULATE (
                Sales[Total Sales],
                PREVIOUSMONTH ( 'Date'[Date] )
            )
        )
    )
    
    """
    assert dax_without_comments == expected_dax

def test_extract_columns_measures(sample_dax):
    processor = DAXProcessor(sample_dax)
    columns_measures = processor.extract_columns_measures()
    assert columns_measures == ["[Total Sales]", "[Date]"]

def test_extract_table_column_references(sample_dax):
    processor = DAXProcessor(sample_dax)
    table_column_references = processor.extract_table_column_references()
    assert table_column_references == [("'Sales'", "[Total Sales]"), ("'Date'", "[Date]")]

if __name__ == "__main__":
    pytest.main()
