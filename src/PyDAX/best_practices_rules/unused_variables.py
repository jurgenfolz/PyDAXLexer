from .best_practice_rule import BestPracticeRule
from ..PyDAXLexer import PyDAXLexer
from antlr4 import Token


rule_metadata = {
    "ID": "UNUSED_VARIABLES",
    "Name": "[DAX Expressions] Unused variables",
    "Category": "DAX Expressions",
    "Description": "Flags variables declared with VAR that are never referenced in the expression.",
    "Severity": 2,
    "short_name": "Unused variable"
}


class UnusedVariables(BestPracticeRule):
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

        tokens: list[Token] = []
        t: Token = self.lexer.nextToken()
        while t.type != Token.EOF:
            if t.channel == Token.DEFAULT_CHANNEL or t.type == PyDAXLexer.VAR:
                tokens.append(t)
            t = self.lexer.nextToken()

        IDENT_LIKE = {
            PyDAXLexer.TABLE_OR_VARIABLE,
        }

        var_defs: dict[str, Token] = {}
        n = len(tokens)
        i = 0
        while i < n:
            tok = tokens[i]
            if tok.type == PyDAXLexer.VAR:
                j = i + 1
                if j < n and tokens[j].type in IDENT_LIKE:
                    name_l = tokens[j].text.lower()
                    var_defs[name_l] = tokens[j]
                    i = j
            i += 1

        if not var_defs:
            self.verified = True
            return

        used: set[str] = set()
        for idx, tok in enumerate(tokens):
            if tok.type in IDENT_LIKE:
                name_l = tok.text.lower()
                if name_l in var_defs and tok is not var_defs[name_l]:
                    used.add(name_l)

        for name_l, def_tok in var_defs.items():
            if name_l not in used:
                self.violators_tokens.append(def_tok)

        self.verified = True
