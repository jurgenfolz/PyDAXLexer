from .DAXToken import DAXToken
from antlr4 import Token
class DAXVariable:
    def __init__(self, name: str, token: Token, var_keyword_token: Token, last_expression_token: Token | None) -> None:
        self.name: str = name
        self.token: DAXToken = DAXToken(token)
        self.var_keyword_token: DAXToken = DAXToken(var_keyword_token)
        self.last_expression_token: DAXToken | None = DAXToken(last_expression_token) if last_expression_token else None

    def __eq__(self, value):
        if isinstance(value, DAXVariable):
            return self.name == value.name and self.token == value.token and self.var_keyword_token == value.var_keyword_token and self.last_expression_token == value.last_expression_token
        return False
    
    def __hash__(self):
        return hash((self.name, self.token, self.var_keyword_token, self.last_expression_token))