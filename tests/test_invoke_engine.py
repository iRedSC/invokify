from invokify import InvokeEngine
import pytest


@pytest.fixture
def engine():
    return InvokeEngine()


def test_create_engine(engine):
    assert engine.commands == {}


def test_create_command(engine):
    @engine.command
    def thing():
        return "hello"

    assert engine.commands["thing"]
    assert thing() == "hello"
