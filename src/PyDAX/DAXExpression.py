from antlr4 import *
from typing import  Any
import html
import warnings

from .PyDAXLexer import PyDAXLexer
from .DAXReference import DAXReference
from .utils import check_contains_function
from .best_practices_rules import *

class DAXExpression:
    
    def __init__(self, dax_expression: str, verify_best_practices: bool = True) -> None:
        
        dax_expression = "" if not isinstance(dax_expression, str) else dax_expression
        self.dax_expression: str = dax_expression
        self.input_stream: InputStream = InputStream(dax_expression)
        
        self.lexer: PyDAXLexer = PyDAXLexer(self.input_stream)
        self.lexer.removeErrorListeners()
        
        self.dax_expression_no_comments: str = self.remove_comments()
        self.table_column_references: list[DAXReference] = self.extract_artifact_references()
        self.comments: list[str] = self.extract_comments()
        self.clean_dax_expression: str = self.clean_expression()
        
        # Initialize best practice rules
        self.best_practice_attributes_initialized: bool = False
        self.init_best_practices_rules()

        if verify_best_practices:
            self.verify_best_practices()
            

    def __str__(self) -> str:
        return self.dax_expression
    
    def __getstate__(self):
        state = self.__dict__.copy()
        # Handle attributes that can't be pickled
        state["input_stream"] = None 
        state["lexer"] = None
        return state

    def __setstate__(self, state):
        #* This fucking thing here is used to handle unpickling of previous versions of the class
        verify_rules = False
        
        # Restore the attributes
        state["input_stream"] = InputStream(state["dax_expression"]) 
        state["lexer"] = PyDAXLexer(state["input_stream"])
        
        #Handles the change from tuples to DAXrefrence objects
        if "table_column_references" in state:
            if isinstance(state["table_column_references"], list):
                if all(isinstance(item, tuple) and len(item) == 2 for item in state["table_column_references"]):
                    state["table_column_references"] = [DAXReference(table_name=t[0], artifact_name=t[1]) for t in state["table_column_references"]]
        
        if not 'best_practice_attributes_initialized' in state:
            state['best_practice_attributes_initialized'] = False
            state['use_divide_function_for_division'] = UseDivide(lexer=state["lexer"])
            state['avoid_using_iferror_function'] = AvoidIfError(lexer=state["lexer"])
            state['use_the_treatas_function_instead_of_intersect'] = UseTreatasInsteadOfIntersect(lexer=state["lexer"])
            state['filter_column_values'] = FilterColumnValues(lexer=state["lexer"])
            state['filter_measure_values_by_columns'] = FilterMeasureValuesByColumns(lexer=state["lexer"])
            state['unused_variables'] = UnusedVariables(lexer=state["lexer"])
            state['avoid_using_1_x_y_syntax'] = AvoidOneMinusDivision(lexer=state["lexer"])
            state['evaluateandlog_should_not_be_used_in_production_models'] = EvaluateAndLogShouldNotBeUsedInProductionModels(lexer=state["lexer"])
            verify_rules = True
        
        
        self.__dict__.update(state)
        
        if verify_rules:
            self.verify_best_practices()
    
    @property
    def best_practice_rules(self) -> list[BestPracticeRule]:
        """Returns a list of all available best practice rules"""
        return [
            self.use_divide_function_for_division,
            self.avoid_using_iferror_function,
            self.use_the_treatas_function_instead_of_intersect,
            self.filter_column_values,
            self.filter_measure_values_by_columns,
            self.unused_variables,
            self.avoid_using_1_x_y_syntax,
            self.evaluateandlog_should_not_be_used_in_production_models,
        ]
    
    @property
    def contains_div(self) -> bool:
        warnings.warn(
            "DAXExpression.contains_div is deprecated and will be removed in a future release. "
            "Use DAXExpression.use_divide_function_for_division directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        return check_contains_function(lexer=self.lexer, function=PyDAXLexer.DIV)

    @property
    def number_of_violations(self) -> int:
        """Returns the total number of best practice violations found in the DAX expression"""
        violations = 0
        for rule in self.best_practice_rules:
            if rule.violated:
                violations += rule.number_of_violations
        
        return violations
    
    
    
    # region #? Best Practices Rules
    
    def init_best_practices_rules(self) -> None:
        """Initializes best practice rules for the DAX expression"""
        self.use_divide_function_for_division: UseDivide = UseDivide(lexer=self.lexer)
        self.avoid_using_iferror_function: AvoidIfError = AvoidIfError(lexer=self.lexer)
        self.use_the_treatas_function_instead_of_intersect: UseTreatasInsteadOfIntersect = UseTreatasInsteadOfIntersect(lexer=self.lexer)
        self.filter_column_values: FilterColumnValues = FilterColumnValues(lexer=self.lexer)
        self.filter_measure_values_by_columns: FilterMeasureValuesByColumns = FilterMeasureValuesByColumns(lexer=self.lexer)
        self.unused_variables: UnusedVariables = UnusedVariables(lexer=self.lexer)
        self.avoid_using_1_x_y_syntax: AvoidOneMinusDivision = AvoidOneMinusDivision(lexer=self.lexer)
        self.evaluateandlog_should_not_be_used_in_production_models: EvaluateAndLogShouldNotBeUsedInProductionModels = EvaluateAndLogShouldNotBeUsedInProductionModels(lexer=self.lexer)
        
    def verify_best_practices(self) -> None:
        for rule in self.best_practice_rules:
            rule.verify_violation()
    
    def print_best_practices_violations(self) -> None:
        """Prints violations of best practice rules"""
        for rule in self.best_practice_rules:
            if rule.violated:
                print(f"Rule Violated: {rule.name} (Severity: {rule.severity})")
                for token in rule.violators_tokens:
                    print(f" - Token: '{token.text}' at line {token.line}, column {token.column}")
    
    
    # endregion #? Best Practices Rules
    
    # region #* DAX Expression Analysis Methods
    
    def print_tokens(self) -> None:
        """Prints all tokens in the DAX expression for debugging purposes"""
        self.lexer.reset()  # Reset the lexer to start from the beginning
        token: Token = self.lexer.nextToken()
        while token.type != Token.EOF:
            print(f"Token Type: {self.lexer.symbolicNames[token.type]}, Text: '{token.text}', Channel: {token.channel}")
            token = self.lexer.nextToken()
    
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
        token: Token = self.lexer.nextToken()
        
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
        token:Token = self.lexer.nextToken()
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
        # First, collect tokens from the default channel
        tokens: list[Token] = []
        token: Token = self.lexer.nextToken()
        while token.type != Token.EOF:
            if token.channel == Token.DEFAULT_CHANNEL:
                tokens.append(token)
            token = self.lexer.nextToken()

        table_column_references: list[DAXReference] = []
        used_column_indexes: set[int] = set()  # columns already paired with a table

        i = 0
        n = len(tokens)
        while i < n:
            token: Token = tokens[i]
            # The good one: TABLE or TABLE_OR_VARIABLE followed by '(' then COLUMN_OR_MEASURE
            if token.type in (PyDAXLexer.TABLE, PyDAXLexer.TABLE_OR_VARIABLE):
                table_name: str = token.text
                j = i + 1
                # Skip a '('
                if j < n and tokens[j].type == PyDAXLexer.OPEN_PARENS:
                    j += 1
                # If next is a column/meaure, pair them
                if j < n and tokens[j].type == PyDAXLexer.COLUMN_OR_MEASURE:
                    artifact_name: str = tokens[j].text
                    # Clean names
                    if artifact_name.endswith(']'):
                        artifact_name = artifact_name[:-1]
                    if artifact_name.startswith('['):
                        artifact_name = artifact_name[1:]
                    if table_name.endswith("'"):
                        table_name = table_name[:-1]
                    if table_name.startswith("'"):
                        table_name = table_name[1:]
                    table_column_references.append(DAXReference(table_name=table_name, artifact_name=artifact_name))
                    used_column_indexes.add(j)
            i += 1

        # Add standalone columns/measures that were not paired with a table
        for idx, token in enumerate(tokens):
            if token.type == PyDAXLexer.COLUMN_OR_MEASURE and idx not in used_column_indexes:
                artifact_name: str = token.text
                if artifact_name.endswith(']'):
                    artifact_name = artifact_name[:-1]
                if artifact_name.startswith('['):
                    artifact_name = artifact_name[1:]
                table_column_references.append(DAXReference(table_name='', artifact_name=artifact_name))

        return table_column_references
    
    # endregion #* DAX Expression Analysis Methods
    
    # region #! DAX Expression HTML Generation Methods
    
    def generate_html(self, name: str = "", light: bool = True) -> str:
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
        prefix = f"{name} = " if name else ""
        html_output = [f'<pre style="font-family: Consolas, monospace; background-color: {colors["background"]}; color: {colors["text_color"]}; padding: 10px;">{prefix}']
        
        self.lexer.reset()
        token: Token = self.lexer.nextToken()
        while token.type != Token.EOF:
            # Prepare display text and escape only HTML control chars (<,' >, &)
            display_text = token.text
            # DAX shows measures/columns in brackets
            if token.type == PyDAXLexer.COLUMN_OR_MEASURE:
                if not (display_text.startswith('[') and display_text.endswith(']')):
                    display_text = f'[{display_text}]'

            safe_text = html.escape(display_text, quote=False)
            if token.type in range(PyDAXLexer.ABS, PyDAXLexer.KEEPFILTERS) or token.type in range(PyDAXLexer.LASTDATE, PyDAXLexer.REL):
                html_output.append(f'<span style="color: {colors["function"]};">{safe_text}</span>')
            elif token.type in [PyDAXLexer.PLUS, PyDAXLexer.MINUS, PyDAXLexer.STAR, PyDAXLexer.DIV, PyDAXLexer.CARET, PyDAXLexer.OP_GE, PyDAXLexer.OP_AND, PyDAXLexer.OP_LE, PyDAXLexer.OP_NE, PyDAXLexer.OP_OR, PyDAXLexer.AND, PyDAXLexer.OR, PyDAXLexer.NOT, PyDAXLexer.COMMA]:
                html_output.append(f'<span style="color: {colors["operator"]};">{safe_text}</span>')
            elif token.type == PyDAXLexer.TABLE:
                html_output.append(f'<span style="color: {colors["table"]};">{safe_text}</span>')
            elif token.type == PyDAXLexer.COLUMN_OR_MEASURE:
                html_output.append(f'<span style="color: {colors["column"]};">{safe_text}</span>')
            elif token.type in [PyDAXLexer.INTEGER_LITERAL, PyDAXLexer.REAL_LITERAL]:
                html_output.append(f'<span style="color: {colors["number"]};">{safe_text}</span>')
            elif token.type in [PyDAXLexer.SINGLE_LINE_COMMENT, PyDAXLexer.DELIMITED_COMMENT]:
                html_output.append(f'<span style="color: {colors["comment"]};">{safe_text}</span>')
            elif token.type == PyDAXLexer.STRING_LITERAL:
                html_output.append(f'<span style="color: {colors["string"]};">{safe_text}</span>')
            else:
                html_output.append(f'<span style="color: {colors["text_color"]};">{safe_text}</span>')
            token = self.lexer.nextToken()
        
        html_output.append('</pre>')
        return ''.join(html_output)
    
    def save_html_to_file(self, file_name: str, name: str = "",light: bool = True) -> None:
        """Saves the generated HTML code to a file."""
        html_code = self.generate_html(name=name, light=light)
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_code)
        print(f"HTML saved to {file_name}")
    
    def generate_html_with_violations(self, name: str = "", light: bool = True) -> str:
        """Generates HTML like generate_html, but highlights best-practice violations.

        For each token listed in any rule's violators_tokens, the corresponding character span
        [token.start, token.stop] in the original expression will be rendered with a light red background.
        """
        #! colors for both modes
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

        colors = dark_mode if not light else light_mode

        # Build a mask of characters that belong to any violation span and map spans to rule names
        expr_text = self.dax_expression or ""
        highlight_mask = [False] * len(expr_text)
        # Map start, stop and rule names for overlapping violations
        violation_spans: dict[tuple[int, int], set[str]] = {}
        for rule in self.best_practice_rules:
            for tok in getattr(rule, 'violators_tokens', []) or []:
                try:
                    start = getattr(tok, 'start', None)
                    stop = getattr(tok, 'stop', None) or getattr(tok, 'end', None)
                    if isinstance(start, int) and isinstance(stop, int) and 0 <= start <= stop < len(highlight_mask):
                        for i in range(start, stop + 1):
                            highlight_mask[i] = True
                        key = (start, stop)
                        names = violation_spans.setdefault(key, set())
                        # use short name for compactness
                        rule_name = f" /*( {rule.short_name} )*/"
                        names.add(str(rule_name))
                except Exception:
                    # skip any token without valid span info
                    continue

        prefix = f"{name} = " if name else ""
        html_output = [f'<pre style="font-family: Consolas, monospace; background-color: {colors["background"]}; color: {colors["text_color"]}; padding: 10px;">{prefix}']

        self.lexer.reset()
        token: Token = self.lexer.nextToken()
        while token.type != Token.EOF:
            # Determine if this token overlaps any violation span
            is_violation = False
            try:
                start = getattr(token, 'start', None)
                stop = getattr(token, 'stop', None)
                if stop is None:
                    stop = getattr(token, 'end', None)
                if isinstance(start, int) and isinstance(stop, int) and 0 <= start <= stop < len(highlight_mask):
                    # if any char in span is highlighted, mark token as violation
                    is_violation = any(highlight_mask[start:stop+1])
            except Exception:
                is_violation = False

            # Prepare display text and escape only HTML control chars (<, >, &)
            display_text = token.text
            if token.type == PyDAXLexer.COLUMN_OR_MEASURE:
                if not (display_text.startswith('[') and display_text.endswith(']')):
                    display_text = f'[{display_text}]'

            safe_text = html.escape(display_text, quote=False)

            # Base color style by token type (same mapping as generate_html)
            if token.type in range(PyDAXLexer.ABS, PyDAXLexer.KEEPFILTERS) or token.type in range(PyDAXLexer.LASTDATE, PyDAXLexer.REL):
                color_style = f'color: {colors["function"]};'
            elif token.type in [PyDAXLexer.PLUS, PyDAXLexer.MINUS, PyDAXLexer.STAR, PyDAXLexer.DIV, PyDAXLexer.CARET, PyDAXLexer.OP_GE, PyDAXLexer.OP_AND, PyDAXLexer.OP_LE, PyDAXLexer.OP_NE, PyDAXLexer.OP_OR, PyDAXLexer.AND, PyDAXLexer.OR, PyDAXLexer.NOT, PyDAXLexer.COMMA]:
                color_style = f'color: {colors["operator"]};'
            elif token.type == PyDAXLexer.TABLE:
                color_style = f'color: {colors["table"]};'
            elif token.type == PyDAXLexer.COLUMN_OR_MEASURE:
                color_style = f'color: {colors["column"]};'
            elif token.type in [PyDAXLexer.INTEGER_LITERAL, PyDAXLexer.REAL_LITERAL]:
                color_style = f'color: {colors["number"]};'
            elif token.type in [PyDAXLexer.SINGLE_LINE_COMMENT, PyDAXLexer.DELIMITED_COMMENT]:
                color_style = f'color: {colors["comment"]};'
            elif token.type == PyDAXLexer.STRING_LITERAL:
                color_style = f'color: {colors["string"]};'
            else:
                color_style = f'color: {colors["text_color"]};'

            # Add violation background if needed and append rule labels after token
            label_html = ''
            if is_violation:
                color_style += ' background-color: #ffcccc;'
                # Aggregate overlapping rule names for this token span
                label_names: set[str] = set()
                if isinstance(start, int) and isinstance(stop, int):
                    for (s, e), names in violation_spans.items():
                        if not (e < start or s > stop):  # overlaps
                            label_names.update(names)
                if label_names:
                    names_text = ', '.join(sorted(label_names))
                    names_text_safe = html.escape(names_text, quote=False)
                    label_html = f'<span style="font-size: 0.8em; color: #666; background-color: #ffcccc; margin-left: 2px;">{names_text_safe}</span>'

            html_output.append(f'<span style="{color_style}">{safe_text}</span>' + label_html)
            token = self.lexer.nextToken()

        html_output.append('</pre>')
        return ''.join(html_output)

    def save_html_with_violations_to_file(self, file_name: str, name: str = "", light: bool = True) -> None:
        """Saves the generated HTML with violation highlights to a file."""
        html_code = self.generate_html_with_violations(name=name, light=light)
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_code)
        print(f"HTML with violations saved to {file_name}")

    # enregion #! DAX Expression HTML Generation Methods
