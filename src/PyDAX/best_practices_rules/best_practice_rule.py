from antlr4 import Token
from ..PyDAXLexer import PyDAXLexer
from typing import Literal
from ..DAXToken import DAXToken

class BestPracticeRule:
    def __init__(self, id: str, name: str, description: str, severity: str, category: str, short_name: str, lexer: PyDAXLexer) -> None:
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.severity: str = severity
        self.category: str = category
        self.short_name: str = short_name
        self.lexer: PyDAXLexer = lexer

        #Verification attr
        self.verified: bool = False
        self.violators_tokens: list[DAXToken] = []
    
    def __str__(self) -> str:
        return f"{self.name} - Verified: {self.verified}, Violations: {len(self.violators_tokens)}"
    
    def __getstate__(self):
        state = self.__dict__.copy()
        # Handle attributes that can't be pickled
        state["lexer"] = None
        return state
    
    @property
    def violated(self) -> bool:
        return len(self.violators_tokens) > 0
    
    @property
    def number_of_violations(self) -> int:
        return len(self.violators_tokens)
    
    
    def clear_violations(self) -> None:
        self.violators_tokens.clear()

    def verify_violation(self, dax_expression) -> None:
        raise NotImplementedError("Subclasses must implement this method")