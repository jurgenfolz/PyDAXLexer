import pytest

from src.PyDAX import (
    DAXArtifactReference,
    DAXFunctionReference,
    DAXTableReference,
    DAXVariableReference,
)


class _FakeToken:
    """Minimal stand-in for antlr4.Token with the fields used by DAXToken.

    Only attributes accessed are: start, stop, line, column, text, type.
    """

    def __init__(self, text: str = "", start: int = 0, stop: int | None = None, line: int = 1, column: int = 0, type: int = 0):
        self.start = start
        # If stop is None, default to start + len(text)
        self.stop = start + (len(text) if stop is None else stop)
        self.line = line
        self.column = column
        self.text = text
        self.type = type


@pytest.fixture
def make_token():
    """Factory fixture that returns a function to build fake tokens.

    Usage: token = make_token(text="MyText")
    """

    def _factory(text: str = "", start: int = 0, stop: int | None = None, line: int = 1, column: int = 0, type: int = 0):
        return _FakeToken(text=text, start=start, stop=stop, line=line, column=column, type=type)

    return _factory


@pytest.fixture
def make_artifact_ref(make_token):
    """Factory for DAXArtifactReference providing minimal tokens.

    Ensures constructor requirements are satisfied while equality remains based on names.
    """

    def _factory(table_name: str, artifact_name: str):
        table_tok = make_token(text=table_name) if table_name is not None and table_name != "" else None
        artifact_tok = make_token(text=artifact_name)
        return DAXArtifactReference(table_name=table_name, artifact_name=artifact_name, artifact_token=artifact_tok, table_token=table_tok)

    return _factory


@pytest.fixture
def make_function_ref(make_token):
    def _factory(name: str):
        return DAXFunctionReference(name=name, token=make_token(text=name))

    return _factory


@pytest.fixture
def make_table_ref(make_token):
    def _factory(name: str):
        return DAXTableReference(name=name, token=make_token(text=name))

    return _factory


@pytest.fixture
def make_variable_ref(make_token):
    def _factory(name: str):
        return DAXVariableReference(name=name, token=make_token(text=name))

    return _factory
