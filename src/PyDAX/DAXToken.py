from antlr4 import Token


class DAXToken:
    def __init__(self, token: Token) -> None:
        self.start: int = token.start
        self.stop: int = token.stop
        self.line: int = token.line
        self.column: int = token.column
        self.text: str = token.text
        self.type: int = token.type

    def __str__(self) -> str:
        return f"Token(Type: {self.type}, Text: '{self.text}', Line: {self.line}, Column: {self.column}, StartIndex: {self.start}, StopIndex: {self.stop})"
    
    