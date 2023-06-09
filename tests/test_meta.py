from typing import Any
from invokify import InvokeEngine, meta, Command
import pytest


@pytest.fixture
def engine():
    return InvokeEngine()


def test_require_engine(engine: InvokeEngine):
    @engine.command
    @meta.require(engine=True)
    def thing(engine: InvokeEngine):
        return engine.commands

    cmd, *_ = engine.parse(["thing"])
    assert thing.requires == {"command": False, "engine": True}
    assert cmd(engine=engine) == {"thing": thing}


def test_require_command(engine: InvokeEngine):
    @engine.command
    @meta.require(command=True)
    def thing(command: Command):
        return command.requires

    cmd, *_ = engine.parse(["thing"])
    assert thing.requires == {"command": True, "engine": False}
    assert cmd() == {"command": True, "engine": False}


def test_require_custom(engine: InvokeEngine):
    @engine.command
    @meta.require(custom=True)
    def thing():
        return "greetings"

    assert thing.requires["custom"] == True


def test_inject_custom(engine: InvokeEngine):
    var = 10

    @engine.command
    @meta.inject(var=var)
    def thing(var: Any):
        return var

    cmd, *_ = engine.parse(["thing"])

    assert cmd() == 10
    assert thing() == 10


def test_help_text(engine: InvokeEngine):
    @engine.command
    @meta.help("This is a command that does a thing.")
    def thing():  # type: ignore
        return "greetings"

    cmd, *_ = engine.parse(["thing"])

    assert cmd.helptext == "This is a command that does a thing."


def test_empty_help_text(engine: InvokeEngine):
    @engine.command
    def thing():  # type: ignore
        return "greetings"

    cmd, *_ = engine.parse(["thing"])

    assert cmd.helptext == None
