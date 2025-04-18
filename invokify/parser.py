from typing import Any
from tokenstream import Token, TokenStream
import re

__all__ = ["string_to_args"]

ESCAPE_REGEX = re.compile(r"\\.")

ESCAPE_SEQUENCES = {
    r"\n": "\n",
    r"\"": '"',
    r"\\": "\\",
}


def unquote_string(token: Token) -> str:
    return ESCAPE_REGEX.sub(lambda match: ESCAPE_SEQUENCES[match[0]], token.value[1:-1])


def parse_list(stream: TokenStream) -> list[Any] | int | float | str | None:
    with stream.syntax(
        comma=r",\s*",
        decimal=r"-?\d*\.\d+|-?\d+\.\d*",
        integer=r"\d+",
        entry=r"[^\"\[\],]+",
    ), stream.ignore("comma"):
        match stream.expect_any(
            "entry", "string", "decimal", "integer", ("brace", "[")
        ):
            case Token(type="brace"):
                return [(parse_list(stream)) for _ in stream.peek_until(("brace", "]"))]
            case Token(type="decimal") as decimal:
                return float(decimal.value)
            case Token(type="integer") as integer:
                return int(integer.value)
            case Token(type="entry") as entry:
                return entry.value
            case Token(type="string") as string:
                return unquote_string(string)
            case _:
                return None


def parse_token(token: Token, stream: TokenStream):
    match token:
        case Token(type="brace"):
            return [(parse_list(stream)) for _ in stream.peek_until(("brace", "]"))]
        case Token(type="string") as string:
            return unquote_string(string)
        case Token(type="decimal") as decimal:
            return float(decimal.value)
        case Token(type="integer") as integer:
            return int(integer.value)
        case Token(type="word") as word:
            return word.value
        case _:
            return None


def string_to_args(string: str):
    stream = TokenStream(string)
    with stream.syntax(
        brace=r"\[|\]",
        decimal=r"-?\d*\.\d+|-?\d+\.\d*",
        integer=r"-?\d+",
        word=r"[^\"\[\]\s]+",
        string=r'"(?:\\.|[^"\\])*"',
    ):
        return [
            parse_token(token, stream)
            for token in stream.collect_any(
                ("brace", "["), "integer", "decimal", "word", "string"
            )
        ]
