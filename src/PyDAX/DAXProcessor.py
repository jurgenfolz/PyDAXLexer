import sys
from antlr4 import *
from .lexer import PyDAXLexer

class DAXProcessor:
    
    def __init__(self, dax_expression):
        self.input_stream = InputStream(dax_expression)
        self.dax_expression = dax_expression
        self.lexer = PyDAXLexer(self.input_stream)
        self.lexer.removeErrorListeners()

    def extract_comments(self) -> list[str]:
        """Extracts comments from the DAX expression

        Returns:
            list[str]: List of comments in the DAX expression
        """
        self.lexer.reset()  # Reset the lexer to start from the beginning
        comments: list[str] = []
        token = self.lexer.nextToken()
        
        while token.type != Token.EOF:
            if token.channel == PyDAXLexer.COMMENTS_CHANNEL:
                comments.append(token.text)
            token = self.lexer.nextToken()
        
        return comments
        
    def remove_comments(self) -> str:
        """Removes comments from the DAX expression

        Returns:
            str: DAX expression without comments
        """
        self.lexer.reset()  # Reset the lexer to start from the beginning
        token = self.lexer.nextToken()
        result: list = []

        while token.type != Token.EOF:
            if token.channel != PyDAXLexer.COMMENTS_CHANNEL:
                result.append(token.text)
            token = self.lexer.nextToken()
        
        return ''.join(result)
    
    def extract_columns_measures(self) -> list[str]:
        """Extracts columns and measures from the DAX expression

        Returns:
            list[str]: List of columns and measures in the DAX expression
        """
        self.lexer.reset()  # Reset the lexer to start from the beginning
        token = self.lexer.nextToken()
        columns_measures: list[str]= []  # Ensure columns_measures list is empty before extraction

        while token.type != Token.EOF:
            if token.type == PyDAXLexer.COLUMN_OR_MEASURE:
                columns_measures.append(token.text)
            token = self.lexer.nextToken()
        
        return columns_measures

    def extract_table_column_references(self) -> list[tuple[str]]:
        """Extracts table and column references from the DAX expression

        Returns:
            list[tuple[str]]: List of table and column references in the DAX expression
        """
        self.lexer.reset()
        table_column_references: list[tuple[str]] = []  # list must be empty before extraction
        token = self.lexer.nextToken()
        while token.type != Token.EOF:
            if token.type == PyDAXLexer.TABLE:  # Match table
                table_name = token.text
                token = self.lexer.nextToken()
                if token.type == PyDAXLexer.OPEN_PARENS:  # Skip '('
                    token = self.lexer.nextToken()
                if token.type == PyDAXLexer.COLUMN_OR_MEASURE:  # Match column
                    column_name = token.text
                    table_column_references.append((table_name, column_name))
            token = self.lexer.nextToken()
        
        return table_column_references