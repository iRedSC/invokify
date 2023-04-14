from invokify import InvokeEngine, string_to_args
import pytest


@pytest.fixture
def engine():
    return InvokeEngine()


def test_string_parsing():
    string = 'single words "multiple words" [words, of, list] [words, "with, comma, but, [in, quotes]"] "[list, in quotes]"'

    result = string_to_args(string)

    assert result == [
        "single",
        "words",
        "multiple words",
        ["words", "of", "list"],
        ["words", "with, comma, but, [in, quotes]"],
        "[list, in quotes]",
    ]


def test_number_parsing():
    nums = "1 2 -54.6 -3 [.6, 6., 98]"

    results = string_to_args(nums)

    assert results == [1, 2, -54.6, -3, [0.6, 6.0, 98]]


def test_parsing_simple(engine):
    @engine.command
    def thing():
        return "hello"

    @thing.subcommand
    def more():
        return "greetings"

    result, *_ = engine.parse(command_list=["thing", "more"])
    result2, *_ = engine.parse(command_list=["thing"])

    assert result() == "greetings"
    assert result2() == "hello"
