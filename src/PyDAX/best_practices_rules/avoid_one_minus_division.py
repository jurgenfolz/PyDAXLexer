
from .best_practice_rule import BestPracticeRule
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token
from ..DAXToken import DAXToken

rule_metadata = {
    "ID": "AVOID_USING_'1-(X/Y)'_SYNTAX",
    "Name": "[DAX Expressions] Avoid using '1-(x/y)' syntax",
    "Category": "DAX Expressions",
    "Description": (
        "Avoid 1 - (x / y) or 1 + (x / y) patterns; prefer DIVIDE and variable precomputation."
    ),
    "Severity": 2,
    "short_name": "Avoid 1-(X/Y) syntax"
}


class AvoidOneMinusDivision(BestPracticeRule):
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
        window: list[Token] = []
        token: Token = self.lexer.nextToken()
        while token.type != Token.EOF:
            if token.channel == Token.DEFAULT_CHANNEL:
                window.append(token)
            token = self.lexer.nextToken()
        for i, t in enumerate(window):
            # Numeric literals are tokenized as INTEGER_LITERAL or REAL_LITERAL
            if t.type in (PyDAXLexer.INTEGER_LITERAL, PyDAXLexer.REAL_LITERAL):
                txt = t.text.strip()
                is_one = False
                try:
                    is_one = float(txt) == 1.0
                except Exception:
                    is_one = False
                if not is_one:
                    continue
                if i + 2 < len(window):
                    op = window[i + 1]
                    # search a '/' within next 10 tokens
                    has_div = any(
                        w.type == PyDAXLexer.DIV for w in window[i + 2 : min(len(window), i + 12)]
                    )
                    if op.type in (PyDAXLexer.PLUS, PyDAXLexer.MINUS) and has_div:
                        self.violators_tokens.append(DAXToken(op))
        self.verified = True
