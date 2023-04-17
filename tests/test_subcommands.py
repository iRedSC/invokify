from invokify import InvokeEngine
import pytest


@pytest.fixture
def engine():
    return InvokeEngine()


def test_create_subcommand(engine: InvokeEngine):
    @engine.command
    def thing():
        ...

    @thing.subcommand
    def more():
        return "hello"

    assert more() == "hello"
    assert more.name == "more"


def test_create_multiple_subcommands(engine: InvokeEngine):
    @engine.command
    def thing():
        ...

    @thing.subcommand
    def more():
        return "hello"

    @more.subcommand
    def even_more():
        return "greetings"

    assert more() == "hello"
    assert even_more() == "greetings"

    cmd, *_ = engine.parse(["thing", "more", "even_more"])
    assert cmd() == "greetings"


def test_stacking_subcommands(engine: InvokeEngine):
    @engine.command
    def thing():
        return "thing"

    @thing.subcommand
    def more():
        return "more"

    @thing.subcommand
    @more.subcommand
    @engine.command
    def extra():  # type: ignore
        return "extra"

    cmd, *_ = engine.parse(["thing", "more"])
    assert cmd() == "more"

    cmd, *_ = engine.parse(["thing", "more", "extra"])
    assert cmd() == "extra"

    cmd, *_ = engine.parse(["thing", "extra"])
    assert cmd() == "extra"

    cmd, *_ = engine.parse(["extra"])
    assert cmd() == "extra"
