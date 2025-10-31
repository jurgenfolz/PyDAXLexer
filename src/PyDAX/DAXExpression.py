from antlr4 import *
from typing import  Any
import html
import warnings

from .PyDAXLexer import PyDAXLexer
from .DAXReference import *
from .DAXVariable import DAXVariable
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
        
        #*Variables
        self.variables: list[DAXVariable] = []
        
        #*References - Expression uses columns, measures, udfs, tables, etc
        self.table_column_references: list[DAXArtifactReference] = []
        
        self.table_references: list[DAXTableReference] = [] #register standalone table references
        self.variable_references: list[DAXVariableReference] = [] #register standalone variable references
        self.function_references: list[DAXFunctionReference] = [] #register standalone function references
        self.unknown_references: list[DAXUnknownReference] = [] #register unknown references, basically a fallback for the others
        
        self.extract_references() #Populkate references
        
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
                    state["table_column_references"] = [DAXArtifactReference(table_name=t[0], artifact_name=t[1]) for t in state["table_column_references"]]
        
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
        
        for rule in self.best_practice_rules:
            rule.lexer = self.lexer
        
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

    def detect_variables(self, tokens: list[Token]) -> set[int]:
        """Detect VAR declarations and populate self.variables.
        """
        self.variables = []
        name_indexes: set[int] = set()

        i = 0
        n = len(tokens)
        while i < n:
            tok = tokens[i]
            # *both VAR tokens and a fallback 'var' if not tokenized as VAR
            #TODO: Review the fallback for lowercase 'var'
            if tok.type == PyDAXLexer.VAR or (isinstance(tok.text, str) and tok.text.upper() == 'VAR'):
                var_keyword_token = tok
                # Find the variable name token: scan ahead to the first identifier-like token
                name_token: Token | None = None
                name_index: int | None = None
                p = i + 1
                while p < n and tokens[p].type not in (PyDAXLexer.ASSIGNMENT, PyDAXLexer.VAR, PyDAXLexer.RETURN):
                    if tokens[p].type in (PyDAXLexer.TABLE_OR_VARIABLE, PyDAXLexer.TABLE):
                        name_token = tokens[p]
                        name_index = p
                        break
                    p += 1
                # Begin scanning expression after name (if found), else after VAR
                j = (name_index + 1) if name_index is not None else (i + 1)
                # Skip '=' if present
                if j < n and tokens[j].type == PyDAXLexer.ASSIGNMENT:
                    j += 1
                # Walk forward to next VAR, RETURN, or EOF to mark last token of expression
                last_expr_token: Token | None = None
                k = j
                while k < n:
                    tk = tokens[k]
                    is_var_kw = (tk.type == PyDAXLexer.VAR) or (isinstance(tk.text, str) and tk.text.upper() == 'VAR')
                    if is_var_kw or tk.type == PyDAXLexer.RETURN:
                        break
                    last_expr_token = tk
                    k += 1
                if name_token is not None:
                    var_name = self._clean_name(name_token.text)
                    self.variables.append(
                        DAXVariable(
                            name=var_name,
                            token=name_token,
                            var_keyword_token=var_keyword_token,
                            last_expression_token=last_expr_token,
                        )
                    )
                    name_indexes.add(name_index)
                i = k
                continue
            i += 1

        return name_indexes
    
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
    
    def extract_references(self) -> None:
        """Extracts table and column references from the DAX expression

        Returns:
            list[tuple[str]]: List of table and column references in the DAX expression
        """
        self.lexer.reset()
        # First, collect tokens from the default and keyword channels (to include VAR/RETURN)
        tokens: list[Token] = []
        token: Token = self.lexer.nextToken()
        while token.type != Token.EOF:
            if token.channel in (Token.DEFAULT_CHANNEL, PyDAXLexer.KEYWORD_CHANNEL):
                tokens.append(token)
            token = self.lexer.nextToken()


        # Detect variables: pattern VAR <name> = <expr> ... until next VAR/RETURN or EOF
        variable_name_token_indexes: set[int] = self.detect_variables(tokens)

        
        used_column_indexes: set[int] = set()  # columns already paired with a table
        used_table_or_variable_indexes: set[int] = set()  # TABLE_OR_VARIABLE tokens already paired with a column
        used_table_indexes: set[int] = set()  # TABLE tokens already paired with a column

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
                    table_name = self._clean_name(table_name)
                    self.table_column_references.append(DAXArtifactReference(table_name=table_name, artifact_name=artifact_name,table_token=token, artifact_token=tokens[j]))
                    used_column_indexes.add(j)
                    # mark table_or_variable as used if it was a TABLE_OR_VARIABLE token
                    if token.type == PyDAXLexer.TABLE_OR_VARIABLE:
                        used_table_or_variable_indexes.add(i)
                    if token.type == PyDAXLexer.TABLE:
                        used_table_indexes.add(i)
            i += 1

        # Add standalone columns/measures that were not paired with a table
        for idx, token in enumerate(tokens):
            if token.type == PyDAXLexer.COLUMN_OR_MEASURE and idx not in used_column_indexes:
                artifact_name: str = token.text
                if artifact_name.endswith(']'):
                    artifact_name = artifact_name[:-1]
                if artifact_name.startswith('['):
                    artifact_name = artifact_name[1:]
                #! In this case we omit the table name and token
                self.table_column_references.append(DAXArtifactReference(table_name='', artifact_name=artifact_name, artifact_token=token))

        #Classify TABLE_OR_VARIABLE and TABLE tokens that are not part of table[column] pairs
        for idx, tok in enumerate(tokens):
            # Skip variable declaration name occurrences
            if idx in variable_name_token_indexes:
                continue
            if tok.type == PyDAXLexer.TABLE_OR_VARIABLE:
                if idx in used_table_or_variable_indexes:
                    # was used as table in a qualified column reference, not a standalone ref
                    continue
                name = self._clean_name(tok.text)
                # Check if this token refers to a declared variable
                is_var = any(var.name == name for var in self.variables)
                if is_var:
                    self.variable_references.append(DAXVariableReference(name=name,token=tok))
                    continue
                # If followed by '(', consider it a (user-defined) function reference
                if idx + 1 < n and tokens[idx + 1].type == PyDAXLexer.OPEN_PARENS:
                    self.function_references.append(DAXFunctionReference(name=name, token=tok))
                    continue
                # Otherwise, consider it a standalone table reference
                self.table_references.append(DAXTableReference(name=name, token=tok))
            elif tok.type == PyDAXLexer.TABLE:
                if idx in used_table_indexes:
                    continue
                name = self._clean_name(tok.text)
                self.table_references.append(DAXTableReference(name=name, token=tok))

        
    
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
            # Prepare display text and escape only HTML control chars
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

        # Build a mask of characters that belong to any violation region and map regions to rule names
        expr_text = self.dax_expression or ""
        highlight_mask = [False] * len(expr_text)
        # Map start, stop and rule names for overlapping violations
        violation_regions: dict[tuple[int, int], set[str]] = {}

        def add_violation_span(start: int, stop: int, label: str) -> None:
            if not isinstance(start, int) or not isinstance(stop, int):
                return
            if not highlight_mask:
                return
            # Clamp to valid range just in case lexer indices are slightly out-of-bounds
            s = max(0, start)
            e = min(len(highlight_mask) - 1, stop)
            if s > e:
                return
            for i in range(s, e + 1):
                highlight_mask[i] = True
            key = (s, e)
            names = violation_regions.setdefault(key, set())
            names.add(str(label))

        for rule in self.best_practice_rules:
            # Use both highlight_tokens (preferred) and violators_tokens directly
            tokens_for_rule = list(rule.highlight_tokens)
            tokens_for_rule.extend(rule.violators_tokens)
            for token in tokens_for_rule:
                try:
                    label = rule.short_name
                    add_violation_span(token.start, token.stop, label)
                except Exception:
                    # skip tokens without valid region info
                    continue

        prefix = f"{name} = " if name else ""
        html_output = [f'<pre style="font-family: Consolas, monospace; background-color: {colors["background"]}; color: {colors["text_color"]}; padding: 10px;">{prefix}']

        self.lexer.reset()
        token: Token = self.lexer.nextToken()
        while token.type != Token.EOF:
            # Determine if this token overlaps any violation region
            is_violation = False
            try:
                start = token.start
                stop = token.stop
                if isinstance(start, int) and isinstance(stop, int) and 0 <= start <= stop < len(highlight_mask):
                    # if any char in region is highlighted, mark token as violation
                    is_violation = any(highlight_mask[start:stop+1])
            except Exception:
                is_violation = False

            # Prepare text and escape HTML control chars (<, >, &)
            display_text = token.text
            if token.type == PyDAXLexer.COLUMN_OR_MEASURE:
                if not (display_text.startswith('[') and display_text.endswith(']')):
                    display_text = f'[{display_text}]'

            safe_text = html.escape(display_text, quote=False)

            #! Colors:
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

            # Add underline style and tooltip for violations
            title_attr = ''
            if is_violation:
                # Force red text for visibility
                # Also add a plain underline
                color_style += (
                    ' color: #ff0000 !important;'
                    ' text-decoration: underline;'
                    ' text-decoration-line: underline;'
                    ' text-decoration-style: wavy;'
                    ' text-decoration-color: #ff0000;'
                    ' -webkit-text-decoration-color: #ff0000;'
                    ' -webkit-text-decoration-style: wavy;'
                    ' text-underline-offset: 2px;'
                    ' cursor: help;'
                )
                # Aggregate overlapping rule names for this token span
                label_names: set[str] = set()
                if isinstance(start, int) and isinstance(stop, int):
                    for (s, e), names in violation_regions.items():
                        if not (e < start or s > stop):  # overlaps
                            label_names.update(names)
                if label_names:
                    names_text = ', '.join(sorted(label_names))
                    names_text_safe = html.escape(names_text, quote=False)
                    title_attr = f' title="{names_text_safe}"'

            html_output.append(f'<span style="{color_style}"{title_attr}>{safe_text}</span>')
            token = self.lexer.nextToken()

        html_output.append('</pre>')
        return ''.join(html_output)

    def save_html_with_violations_to_file(self, file_name: str, name: str = "", light: bool = True) -> None:
        """Saves the generated HTML with violation highlights to a file."""
        html_code = self.generate_html_with_violations(name=name, light=light)
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html_code)
        print(f"HTML with violations saved to {file_name}")

    # endregion #! DAX Expression HTML Generation Methods

    # region #? Helper Methods
    
    @staticmethod
    def _clean_name(text: str) -> str:
        if text.endswith("'"):
            text = text[:-1]
        if text.startswith("'"):
            text = text[1:]
        return text

    # endregion #? Helper Methods