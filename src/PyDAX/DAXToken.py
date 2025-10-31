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
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DAXToken):
            return False
        return (self.start == other.start and
                self.stop == other.stop and
                self.line == other.line and
                self.column == other.column and
                self.text == other.text and
                self.type == other.type)
        
    def __hash__(self) -> int:
        return hash((self.start, self.stop, self.line, self.column, self.text, self.type))