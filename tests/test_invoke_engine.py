from invokify import InvokeEngine
import pytest


@pytest.fixture
def engine():
    return InvokeEngine()


def test_create_engine(engine: InvokeEngine):
    assert engine.commands == {}


def test_create_command(engine: InvokeEngine):
    @engine.command
    def thing():
        return "hello"

    assert engine.commands["thing"]
    assert thing() == "hello"
