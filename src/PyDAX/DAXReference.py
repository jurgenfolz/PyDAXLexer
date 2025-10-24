

class DAXReference:
    def __init__(self, table_name: str, artifact_name: str):
        self.table_name = table_name
        self.artifact_name = artifact_name

    def __str__(self):
        return f"'{self.table_name}'[{self.artifact_name}]"


    def __eq__(self, value):
        if isinstance(value, DAXReference):
            return self.table_name == value.table_name and self.artifact_name == value.artifact_name
        return False
    
    def __hash__(self):
        return hash((self.table_name, self.artifact_name))