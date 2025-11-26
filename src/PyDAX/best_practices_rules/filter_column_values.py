import re
from .best_practice_rule import BestPracticeRule
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token
from ..DAXToken import DAXToken

#! Limitation: Currently n ot checking for multiple violations on the same expression

rule_metadata = {
    "ID": "FILTER_COLUMN_VALUES",
    "Name": "[DAX Expressions] Filter column values with proper syntax",
    "Category": "DAX Expressions",
    "Description": (
        "Prefer KEEPFILTERS('Table'[Column] = \"Value\") or 'Table'[Column] = \"Value\" over FILTER('Table', 'Table'[Column] = \"Value\")."
    ),
    "Severity": 2,
    "short_name": "Prefer KEEPFILTERS('Table'[Column] = Value) or 'Table'[Column] = Value over FILTER('Table', 'Table'[Column] = Value)."
}


class FilterColumnValues(BestPracticeRule):
    def __init__(self) -> None:
        super().__init__(
            id=rule_metadata["ID"],
            name=rule_metadata["Name"],
            description=rule_metadata["Description"],
            severity=str(rule_metadata["Severity"]),
            category=rule_metadata["Category"],
            short_name=rule_metadata["short_name"]
        )
        self.patterns = [
            re.compile(r"CALCULATE\s*\(\s*[^,]+,\s*FILTER\s*\(\s*'?[A-Za-z0-9 _]+'?\s*,\s*'?[A-Za-z0-9 _]+'?\[[A-Za-z0-9 _]+\]", re.IGNORECASE),
            re.compile(r"CALCULATETABLE\s*\([^,]*,\s*FILTER\s*\(\s*'?[A-Za-z0-9 _]+'?,\s*'?[A-Za-z0-9 _]+'?\[[A-Za-z0-9 _]+\]", re.IGNORECASE),
        ]

    def verify_violation(self, lexer: "PyDAXLexer") -> None:
        self.clear_violations()
        lexer.reset()

        full_text = lexer.inputStream.strdata

        # Token-based guard: require a real CALCULATE/CALCULATETABLE token on the keyword channel
        # (ignores commented occurrences). Also prepare tokens for span expansion.
        lexer.reset()
        all_tokens: list[Token] = lexer.getAllTokens()
        # Tokens on the keyword channel (functions like CALCULATE, FILTER)
        keyword_tokens: list[Token] = [t for t in all_tokens if t.channel == PyDAXLexer.KEYWORD_CHANNEL]
        # Tokens we can use to expand highlight spans (default + keyword channels)
        search_tokens: list[Token] = [
            t for t in all_tokens if t.channel in (Token.DEFAULT_CHANNEL, PyDAXLexer.KEYWORD_CHANNEL)
        ]
        
        #* checks if there is a CALCULATE or CALCULATETABLE token that is not commented out (thats why we use KEYWORD_CHANNEL)
        has_calculate = any(
            token.type in (PyDAXLexer.CALCULATE, PyDAXLexer.CALCULATETABLE) for token in keyword_tokens
        )
        if not has_calculate:
            self.verified = True
            return

        filter_tokens = [token for token in keyword_tokens if token.type == PyDAXLexer.FILTER]

        # Track added highlight spans to avoid duplicates
        seen_highlights: set[tuple[int, int]] = set()

        for pattern in self.patterns:
            for match in pattern.finditer(full_text):
                match_start, match_end = match.span()

                for ft in filter_tokens:
                    if ft.start >= match_start and ft.stop < match_end:
                        # Count only the FILTER token as the violation
                        if ft not in self.violators_tokens:
                            self.violators_tokens.append(DAXToken(ft))
                        # Always highlight FILTER itself
                        key = (ft.start, ft.stop)
                        if key not in seen_highlights:
                            self.highlight_tokens.append(DAXToken(ft))
                            seen_highlights.add(key)

                        # Find the first COLUMN_OR_MEASURE token after FILTER within match span
                        column_tok = None
                        for t in search_tokens:
                            if (
                                t.type == PyDAXLexer.COLUMN_OR_MEASURE
                                and t.start > ft.start
                                and t.stop <= match_end
                            ):
                                column_tok = t
                                break

                        # If present, add all tokens from FILTER .. column to highlight list only
                        if column_tok is not None:
                            end_idx = column_tok.stop
                            for t in search_tokens:
                                if t.start >= ft.start and t.stop <= end_idx:
                                    key = (t.start, t.stop)
                                    if key not in seen_highlights:
                                        self.highlight_tokens.append(DAXToken(t))
                                        seen_highlights.add(key)
        
        self.verified = True
