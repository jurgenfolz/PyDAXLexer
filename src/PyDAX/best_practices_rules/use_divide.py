from .best_practice_rule import BestPracticeRule
from ..utils import check_contains_function
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token

rule_metadata = {
      "ID": "USE_THE_DIVIDE_FUNCTION_FOR_DIVISION",
      "Name": "[DAX Expressions] Use the DIVIDE function for division",
      "Category": "DAX Expressions",
      "Description": "Use the DIVIDE  function instead of using \"/\". The DIVIDE function resolves divide-by-zero cases. As such, it is recommended to use to avoid errors.\r\n\r\nReference: https://docs.microsoft.com/power-bi/guidance/dax-divide-function-operator",
      "Severity": 2,
      "short_name": "Use DIVIDE instead of /"
}



class UseDivide(BestPracticeRule):
    def __init__(self, lexer: 'PyDAXLexer') -> None:
        # Initialize the base BestPracticeRule with metadata
        super().__init__(
            id=rule_metadata["ID"],
            name=rule_metadata["Name"],
            description=rule_metadata["Description"],
            severity=rule_metadata["Severity"],
            category=rule_metadata["Category"],
            short_name=rule_metadata["short_name"],
            lexer=lexer
        )


    def verify_violation(self) -> None:
        # Check if the DAX expression contains the division operator
        self.clear_violations()
        self.lexer.reset()  # Reset the lexer to start from the beginning
        token: Token = self.lexer.nextToken()

        while token.type != Token.EOF:
            if token.type == PyDAXLexer.DIV:
                self.violators_tokens.append(token)
                
            token = self.lexer.nextToken()
        
        self.verified = True

