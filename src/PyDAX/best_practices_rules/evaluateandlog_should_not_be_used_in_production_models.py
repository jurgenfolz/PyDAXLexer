from .best_practice_rule import BestPracticeRule
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token
from ..DAXToken import DAXToken

rule_metadata = {
    "ID": "EVALUATEANDLOG_SHOULD_NOT_BE_USED_IN_PRODUCTION_MODELS",
    "Name": "[DAX Expressions] The EVALUATEANDLOG function should not be used in production models",
    "Category": "DAX Expressions",
    "Description": (
        "The EVALUATEANDLOG function is meant for development/test environments and should not be used in production models."
    ),
    "Severity": 1,
    "short_name": "EVALUATEANDLOG should not be used"
}


class EvaluateAndLogShouldNotBeUsedInProductionModels(BestPracticeRule):
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
            if token.type == PyDAXLexer.EVALUATEANDLOG:
                self.violators_tokens.append(DAXToken(token))
            token = self.lexer.nextToken()
        self.verified = True
