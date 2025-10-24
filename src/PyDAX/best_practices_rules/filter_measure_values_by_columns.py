from .best_practice_rule import BestPracticeRule
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token


rule_metadata = {
    "ID": "FILTER_MEASURE_VALUES_BY_COLUMNS",
    "Name": "[DAX Expressions] Filter measure values by columns, not tables",
    "Category": "DAX Expressions",
    "Description": (
        "Prefer FILTER over VALUES/ALL('Table'[Column]) for measure filters rather than filtering entire tables."
    ),
    "Severity": 2,
    "short_name": "Filter measure values by columns"
}


class FilterMeasureValuesByColumns(BestPracticeRule):
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
