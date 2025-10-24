from .best_practice_rule import BestPracticeRule
from ..utils import check_contains_function
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token



rule_metadata = {
      "ID": "AVOID_USING_THE_IFERROR_FUNCTION",
      "Name": "[DAX Expressions] Avoid using the IFERROR function",
      "Category": "DAX Expressions",
      "Description": "Avoid using the IFERROR function as it may cause performance degradation. If you are concerned about a divide-by-zero error, use the DIVIDE function as it naturally resolves such errors as blank (or you can customize what should be shown in case of such an error).\r\nReference: https://www.elegantbi.com/post/top10bestpractices",
      "Severity": 2,
      "short_name": "Avoid IFERROR"
    }

class AvoidIfError(BestPracticeRule):
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
        # Check if the DAX expression contains the IFERROR function
        self.clear_violations()
        self.lexer.reset()  # Reset the lexer to start from the beginning
        token: Token = self.lexer.nextToken()

        while token.type != Token.EOF:
            if token.type == PyDAXLexer.IFERROR:
                self.violators_tokens.append(token)
                
            token = self.lexer.nextToken()
        
        self.verified = True