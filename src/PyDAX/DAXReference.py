from antlr4 import Token
from .DAXToken import DAXToken
class DAXArtifactReference:
    def __init__(self, table_name: str, artifact_name: str, artifact_token: Token, table_token: Token = None):
        self.table_name = table_name
        self.artifact_name = artifact_name
        self.table_token: DAXToken | None = DAXToken(table_token) if table_token else None #Can be empty for measures without a table reference
        self.artifact_token: DAXToken = DAXToken(artifact_token)

    def __str__(self):
        return f"'{self.table_name}'[{self.artifact_name}]"


    def __eq__(self, value):
        if isinstance(value, DAXArtifactReference):
            return self.table_name == value.table_name and self.artifact_name == value.artifact_name
        return False
    
    def __hash__(self):
        return hash((self.table_name, self.artifact_name))
    
    
class DAXReference:
    def __init__(self, name: str, token: Token):
        self.name: str = name
        self.token: DAXToken = DAXToken(token)

    def __str__(self):
        return self.name


    def __eq__(self, value):
        if isinstance(value, DAXReference):
            return self.name == value.name
        return False
    
    def __hash__(self):
        return hash(self.name)
    

class DAXTableReference(DAXReference):
    def __init__(self, name: str, token: Token):
        super().__init__(name, token)

class DAXVariableReference(DAXReference):
    def __init__(self, name: str, token: Token):
        super().__init__(name, token)
   
    
class DAXFunctionReference(DAXReference):
    def __init__(self, name: str, token: Token):
        super().__init__(name, token)

class DAXUnknownReference(DAXReference):
    def __init__(self, name: str, token: Token):
        super().__init__(name, token)