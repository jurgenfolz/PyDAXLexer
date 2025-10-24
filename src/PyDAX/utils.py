from antlr4 import Token
from typing import Any
from .PyDAXLexer import PyDAXLexer


def check_contains_function(lexer: PyDAXLexer, function: Any) -> bool:
        lexer.reset()  # Reset the lexer to start from the beginning
        token: Token = lexer.nextToken()
         
        while token.type != Token.EOF:
            if token.type == function:
                return True
            token = lexer.nextToken()
        return False