from invokify import InvokeEngine, CommandAlreadyExists
import pytest


@pytest.fixture
def engine():
    return InvokeEngine()


def test_adding_multiple_aliases(engine: InvokeEngine):
    @engine.command
    def thing():  # type: ignore
        return "hello"

    with pytest.raises(CommandAlreadyExists):

        @engine.command(name="thing")
        def more():  # type: ignore
            return "greeting"


def test_adding_duplicate_aliases(engine: InvokeEngine):
    @engine.command(aliases=["other", "cool"])
    def thing():  # type: ignore
        return "hello"

    with pytest.raises(CommandAlreadyExists):

        @engine.command(aliases=["cool"])
        def more():  # type: ignore
            return "greeting"


def test_aliases(engine: InvokeEngine):
    @engine.command(aliases=["other", "cool"])
    def thing():
        return "hello"

    @thing.subcommand(aliases=["special", "stuff"])
    def more():  # type: ignore
        return "greetings"

    assert engine.parse(["other"])[0]() == "hello"
    assert engine.parse(["special"])[0] == None
    assert engine.parse(["cool", "stuff"])[0]() == "greetings"
    assert engine.parse(["other", "stuff"])[0]() == "greetings"
    assert engine.parse(["cool", "special"])[0]() == "greetings"
    assert engine.parse(["cool", "more"])[0]() == "greetings"
    assert engine.parse(["thing", "stuff"])[0]() == "greetings"


def test_command_in_class(engine: InvokeEngine):
    class Guy:
        def __init__(self):
            self.money = 0

        @engine.command
        def buy(self, amount: int):
            self.money -= amount
            return self.money

        @buy.subcommand(name="all")
        def buy_all(self):
            self.money = 0
            return self.money

        @engine.command
        def sell(self, amount: int):
            self.money += amount
            return self.money

    guy = Guy()

    cmd, args, _ = engine.parse(["sell", 100])
    assert cmd(guy, *args) == 100

    cmd, args, _ = engine.parse(["buy", 50])
    assert cmd(guy, *args) == 50

    cmd, args, _ = engine.parse(["buy", "all"])
    assert cmd(guy, *args) == 0


def test_multiple_engines():
    engine1 = InvokeEngine()
    engine2 = InvokeEngine()
    engine3 = InvokeEngine()

    @engine3.command(aliases=["extra", "stuff"])
    @engine2.command(name="more")
    @engine1.command
    def thing():  # type: ignore
        return "greetings"

    cmd, *_ = engine1.parse(["thing"])
    assert cmd() == "greetings"

    cmd, *_ = engine2.parse(["more"])
    assert cmd() == "greetings"

    cmd, *_ = engine3.parse(["stuff"])
    assert cmd() == "greetings"
