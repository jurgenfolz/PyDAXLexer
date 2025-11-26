from .best_practice_rule import BestPracticeRule
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token
from ..DAXToken import DAXToken

rule_metadata = {
    "ID": "USE_THE_TREATAS_FUNCTION_INSTEAD_OF_INTERSECT",
    "Name": "[DAX Expressions] Use the TREATAS function instead of INTERSECT for virtual relationships",
    "Category": "DAX Expressions",
    "Description": (
        "The TREATAS function is more efficient and provides better performance than the INTERSECT function when used in virutal relationships."
    ),
    "Severity": 2,
    "short_name": "Use TREATAS instead of INTERSECT"
}


class UseTreatasInsteadOfIntersect(BestPracticeRule):
    def __init__(self) -> None:
        super().__init__(
            id=rule_metadata["ID"],
            name=rule_metadata["Name"],
            description=rule_metadata["Description"],
            severity=str(rule_metadata["Severity"]),
            category=rule_metadata["Category"],
            short_name=rule_metadata["short_name"],
        )

    def verify_violation(self, lexer: "PyDAXLexer") -> None:
        self.clear_violations()
        lexer.reset()
        token: Token = lexer.nextToken()
        while token.type != Token.EOF:
            if token.type == PyDAXLexer.INTERSECT:
                self.violators_tokens.append(DAXToken(token))
                self.highlight_tokens.append(DAXToken(token))
            token = lexer.nextToken()
        self.verified = True
