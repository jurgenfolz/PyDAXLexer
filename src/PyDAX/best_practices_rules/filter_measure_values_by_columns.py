import re
from .best_practice_rule import BestPracticeRule
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token
from ..DAXToken import DAXToken

#! Limitation: Currently n ot checking for multiple violations on the same expression

rule_metadata = {
    "ID": "FILTER_MEASURE_VALUES_BY_COLUMNS",
    "Name": "[DAX Expressions] Filter measure values by columns, not tables",
    "Category": "DAX Expressions",
    "Description": (
        "Prefer FILTER over VALUES/ALL('Table'[Column]) for measure filters rather than filtering entire tables."
    ),
    "Severity": 2,
    "short_name": "Prefer FILTER over VALUES/ALL('Table'[Column]) for measure filters rather than filtering entire tables"
}


class FilterMeasureValuesByColumns(BestPracticeRule):
    def __init__(self) -> None:
        super().__init__(
            id=rule_metadata["ID"],
            name=rule_metadata["Name"],
            description=rule_metadata["Description"],
            severity=str(rule_metadata["Severity"]),
            category=rule_metadata["Category"],
            short_name=rule_metadata["short_name"],
        )
        self.patterns = [
            re.compile(
                r"CALCULATE\s*\(\s*[^,]+,\s*FILTER\s*\(\s*'?[A-Za-z0-9 _]+'?\s*,\s*\[[^\]]+\]",
                re.IGNORECASE,
            ),
            re.compile(
                r"CALCULATETABLE\s*\([^,]*,\s*FILTER\s*\(\s*'?[A-Za-z0-9 _]+'?\s*,\s*\[",
                re.IGNORECASE,
            ),
        ]

    def verify_violation(self, lexer: "PyDAXLexer") -> None:
        self.clear_violations()
        lexer.reset()

        full_text = lexer.inputStream.strdata
        # Make sure that the expression contains a CALCULATE or CALCULATETABLE outside of comments/strings
        lexer.reset()
        all_tokens: list[Token] = lexer.getAllTokens()
        keyword_tokens = [t for t in all_tokens if t.channel == PyDAXLexer.KEYWORD_CHANNEL]
        has_calculate = any(
            t.type in (PyDAXLexer.CALCULATE, PyDAXLexer.CALCULATETABLE) for t in keyword_tokens
        )
        if not has_calculate:
            self.verified = True
            return

        filter_tokens = [t for t in keyword_tokens if t.type == PyDAXLexer.FILTER]

        # Find all violations via regex spans and map them to FILTER tokens by position
        for pattern in self.patterns:
            for match in pattern.finditer(full_text):
                start, end = match.span()
                for ft in filter_tokens:
                    if ft.start >= start and ft.stop < end:
                        if ft not in self.violators_tokens:
                            self.violators_tokens.append(DAXToken(ft))
                            self.highlight_tokens.append(DAXToken(ft))

        self.verified = True
