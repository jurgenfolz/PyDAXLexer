from .best_practice_rule import BestPracticeRule
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token


rule_metadata = {
    "ID": "FILTER_COLUMN_VALUES",
    "Name": "[DAX Expressions] Filter column values with proper syntax",
    "Category": "DAX Expressions",
    "Description": (
        "Prefer KEEPFILTERS('Table'[Column] = \"Value\") or 'Table'[Column] = \"Value\" over FILTER('Table', 'Table'[Column] = \"Value\")."
    ),
    "Severity": 2,
    "short_name": "Filter column values with proper syntax"
}


class FilterColumnValues(BestPracticeRule):
    def __init__(self, lexer: "PyDAXLexer") -> None:
        super().__init__(
            id=rule_metadata["ID"],
            name=rule_metadata["Name"],
            description=rule_metadata["Description"],
            severity=str(rule_metadata["Severity"]),
            category=rule_metadata["Category"],
            short_name=rule_metadata["short_name"],
            lexer=lexer,
        )

    def verify_violation(self) -> None:
        self.clear_violations()
        self.lexer.reset()
        token: Token = self.lexer.nextToken()
        while token.type != Token.EOF:
            if token.type == PyDAXLexer.FILTER:
                self.violators_tokens.append(token)
            token = self.lexer.nextToken()
        self.verified = True
