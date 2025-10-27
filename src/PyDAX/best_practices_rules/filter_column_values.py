import re
from .best_practice_rule import BestPracticeRule
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token

#! Limitation: Currently n ot checking for multiple violations on the same expression

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
        self.patterns = [
            re.compile(r"CALCULATE\s*\(\s*[^,]+,\s*FILTER\s*\(\s*'?[A-Za-z0-9 _]+'?\s*,\s*'?[A-Za-z0-9 _]+'?\[[A-Za-z0-9 _]+\]", re.IGNORECASE),
            re.compile(r"CALCULATETABLE\s*\([^,]*,\s*FILTER\s*\(\s*'?[A-Za-z0-9 _]+'?,\s*'?[A-Za-z0-9 _]+'?\[[A-Za-z0-9 _]+\]", re.IGNORECASE),
        ]

    def verify_violation(self) -> None:
        self.clear_violations()
        self.lexer.reset()

        full_text = self.lexer.inputStream.strdata

        # Token-based guard: require a real CALCULATE/CALCULATETABLE token on the default channel.
        # This avoids matching when those keywords appear only inside comments or strings.
        self.lexer.reset()
        all_tokens: list[Token] = self.lexer.getAllTokens()
        #Put all KEYWORD tokens in a list
        default_tokens = [token for token in all_tokens if token.channel == PyDAXLexer.KEYWORD_CHANNEL]
        
        #* checks if there is a CALCULATE or CALCULATETABLE token that is not commented out (thats why we use KEYWORD_CHANNEL)
        has_calculate = any(
            token.type in (PyDAXLexer.CALCULATE, PyDAXLexer.CALCULATETABLE) for token in default_tokens
        )
        if not has_calculate:
            self.verified = True
            return

        filter_tokens = [token for token in default_tokens if token.type == PyDAXLexer.FILTER]

        for pattern in self.patterns:
            for match in pattern.finditer(full_text):
                match_start, match_end = match.span()

                for ft in filter_tokens:
                    if ft.start >= match_start and ft.stop < match_end:
                        if ft not in self.violators_tokens:
                            self.violators_tokens.append(ft)
        
        self.verified = True
