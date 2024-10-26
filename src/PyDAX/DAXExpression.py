import sys
from antlr4 import *
from .lexer import PyDAXLexer

class DAXExpression:
    
    def __init__(self, dax_expression: str):
        dax_expression = "" if not isinstance(dax_expression, str) else dax_expression
        self.dax_expression: str = dax_expression
        self.input_stream: InputStream = InputStream(dax_expression)
        self.lexer: PyDAXLexer = PyDAXLexer(self.input_stream)
        self.lexer.removeErrorListeners()
        self.dax_expression_no_comments: str = self.remove_comments()
        self.table_column_references: list[tuple[str, str]] = self.extract_artifact_references()
        self.comments: list[str] = self.extract_comments()
        self.clean_dax_expression = self.clean_expression()
        self.contains_div = self.check_contains_div()
    
    def __str__(self) -> str:
        return self.dax_expression
    
    def __getstate__(self):
        state = self.__dict__.copy()
        # Handle attributes that can't be pickled
        state["input_stream"] = None 
        state["lexer"] = None
        return state

    def __setstate__(self, state):
        # Restore the attributes
        state["input_stream"] = InputStream(state["dax_expression"]) 
        state["lexer"] = PyDAXLexer(state["input_stream"])
        self.__dict__.update(state)
    
    
    def check_contains_div(self):
        self.lexer.reset()  # Reset the lexer to start from the beginning
        token = self.lexer.nextToken() 
        while token.type != Token.EOF:
            if token.type == PyDAXLexer.DIV:
                return True
            token = self.lexer.nextToken()
        return False
    
    def clean_expression(self) -> str:
        """Cleans the DAX expression by removing whitespaces, tabs, newlines, and carriage returns

        Returns:
            str: The cleaned DAX expression
        """
        return self.dax_expression_no_comments.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")

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
    
    def extract_artifact_references(self) -> list[tuple[str, str]]:
        """Extracts table and column references from the DAX expression

        Returns:
            list[tuple[str]]: List of table and column references in the DAX expression
        """
        self.lexer.reset()
        table_column_references: list[tuple[str]] = []  # list must be empty before extraction
        token = self.lexer.nextToken()
        while token.type != Token.EOF:
            if token.type == PyDAXLexer.TABLE or token.type == PyDAXLexer.TABLE_OR_VARIABLE:  # Match table
                table_name: str = token.text
                token: Token = self.lexer.nextToken()
                if token.type == PyDAXLexer.OPEN_PARENS:  # Skip '('
                    token = self.lexer.nextToken()
                if token.type == PyDAXLexer.COLUMN_OR_MEASURE:  # Match column
                    artifact_name: str = token.text # Store column name
                    #Clean up artifact name
                    artifact_name = artifact_name[:-1] if artifact_name.endswith(']') else artifact_name # Remove closing bracket
                    artifact_name = artifact_name[1:] if artifact_name.startswith('[') else artifact_name # Remove opening bracket
                    
                    #clean up table name
                    table_name = table_name[:-1] if table_name.endswith("'") else table_name
                    table_name = table_name[1:] if table_name.startswith("'") else table_name
                    
                    # Append table and column reference to the list
                    table_column_references.append((table_name, artifact_name))
                

            #* References without table name
            elif token.type == PyDAXLexer.COLUMN_OR_MEASURE:
                artifact_name: str = token.text # Store column or measure name
                artifact_name = artifact_name[:-1] if artifact_name.endswith(']') else artifact_name
                artifact_name = artifact_name[1:] if artifact_name.startswith('[') else artifact_name
                table_column_references.append(("", artifact_name))
                
            
                
            token = self.lexer.nextToken()
        
        return table_column_references

    def generate_html(self, light: bool) -> str:
        """Generates an HTML string with colorized DAX elements in light or dark mode"""
        
        # Define colors for both modes
        dark_mode = {
            'background': '#333',
            'text_color': '#D4D4D4',
            'function': '#B469FF',
            'operator': '#D4D4D4',
            'table': '#1E90FF',
            'column': '#4EC9B0',
            'number': '#B5CEA8',
            'comment': '#6A9955',
            'string': '#D69D85',
        }
        
        light_mode = {
            'background': '#FFFFFF',
            'text_color': '#000000',
            'function': '#7959C1',
            'operator': '#333333',
            'table': '#0063B1',
            'column': '#00796B',
            'number': '#008000',
            'comment': '#008000',
            'string': '#D9534F',
        }
        
        # Choose the color set based on the mode
        colors = dark_mode if not light else light_mode
        
        # HTML template
        html_output = [f'<pre style="font-family: Consolas, monospace; background-color: {colors["background"]}; color: {colors["text_color"]}; padding: 10px;">']
        
        self.lexer.reset()
        token: Token = self.lexer.nextToken()
        while token.type != Token.EOF:
            if token.type in range(PyDAXLexer.ABS, PyDAXLexer.KEEPFILTERS) or token.type in range(PyDAXLexer.LASTDATE, PyDAXLexer.REL):
                html_output.append(f'<span style="color: {colors["function"]};">{token.text}</span>')
            elif token.type in [PyDAXLexer.PLUS, PyDAXLexer.MINUS, PyDAXLexer.STAR, PyDAXLexer.DIV, PyDAXLexer.CARET, PyDAXLexer.OP_GE, PyDAXLexer.OP_AND, PyDAXLexer.OP_LE, PyDAXLexer.OP_NE, PyDAXLexer.OP_OR, PyDAXLexer.AND, PyDAXLexer.OR, PyDAXLexer.NOT, PyDAXLexer.COMMA]:
                html_output.append(f'<span style="color: {colors["operator"]};">{token.text}</span>')
            elif token.type == PyDAXLexer.TABLE:
                html_output.append(f'<span style="color: {colors["table"]};">{token.text}</span>')
            elif token.type == PyDAXLexer.COLUMN_OR_MEASURE:
                html_output.append(f'<span style="color: {colors["column"]};">{token.text}</span>')
            elif token.type in [PyDAXLexer.INTEGER_LITERAL, PyDAXLexer.REAL_LITERAL]:
                html_output.append(f'<span style="color: {colors["number"]};">{token.text}</span>')
            elif token.type in [PyDAXLexer.SINGLE_LINE_COMMENT, PyDAXLexer.DELIMITED_COMMENT]:
                html_output.append(f'<span style="color: {colors["comment"]};">{token.text}</span>')
            elif token.type == PyDAXLexer.STRING_LITERAL:
                html_output.append(f'<span style="color: {colors["string"]};">{token.text}</span>')
            else:
                html_output.append(f'<span style="color: {colors["text_color"]};">{token.text}</span>')
            token = self.lexer.nextToken()
        
        html_output.append('</pre>')
        return ''.join(html_output)
    
    def save_html_to_file(self, file_name: str) -> None:
        """Saves the generated HTML code to a file."""
        html_code = self.generate_html()
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_code)
        print(f"HTML saved to {file_name}")
    