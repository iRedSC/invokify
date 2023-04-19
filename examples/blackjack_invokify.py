from dataclasses import dataclass, field
from enum import Enum, auto
import random
from typing import Iterable
from invokify import InvokeEngine, string_to_args
import itertools
from collections import deque


class SUIT(Enum):
    DIAMONDS = auto()
    CLUBS = auto()
    HEARTS = auto()
    SPADES = auto()


class GAME_RESULT(Enum):
    WIN = auto()
    LOSE = auto()
    DRAW = auto()


@dataclass(slots=True)
class Card:
    suit: SUIT
    value: int | Iterable[
        int
    ]  # Can hold multiple values, the highest value that won't bust will be chosen.

    def __repr__(self) -> str:
        return f"Card({self.suit}, {self.value})"


@dataclass(slots=True)
class BlackJack:
    deck: list[Card]
    dealer: list[Card] = field(default_factory=list)
    player: list[Card] = field(default_factory=list)

    def __post_init__(self):
        self.deck = deque(self.deck)
        for _ in range(2):
            self.hit(self.dealer)
            self.hit(self.player)

    def get_hand_value(self, player: list[Card]):
        total_value = 0
        aces_count = 0

        for card in player:
            if isinstance(card.value, int):
                total_value += card.value
            else:
                aces_count += 1
                total_value += min(
                    card.value
                )  # Add the lowest value of the multi-value card (Ace: 1)

        # Try to add 10 (11 - 1) for each Ace without exceeding 21
        for _ in range(aces_count):
            if total_value + 10 <= 21:
                total_value += 10

        return total_value

    def hit(self, player: list):
        player.append(self.deck.pop())

    def flip(self):
        player_hand = self.get_hand_value(self.player)
        dealer_hand = self.get_hand_value(self.dealer)

        if player_hand > 21 and dealer_hand > 21:
            return GAME_RESULT.DRAW
        if dealer_hand > 21 and player_hand <= 21:
            return GAME_RESULT.WIN
        if player_hand > dealer_hand and player_hand <= 21:
            return GAME_RESULT.WIN
        return GAME_RESULT.LOSE

    def dealer_hit(self):
        while self.get_hand_value(self.dealer) <= 16:
            self.hit(self.dealer)


def create_deck() -> list[Card]:
    deck = []
    for suit in (SUIT.DIAMONDS, SUIT.CLUBS, SUIT.HEARTS, SUIT.SPADES):
        for value in range(1, 14):
            if value > 10:
                value = 10
            if value == 1:
                value = (1, 11)

            deck.append(Card(suit=suit, value=value))
    return deck


engine = InvokeEngine()


@engine.command
def hit(*_, game: BlackJack) -> tuple[GAME_RESULT, str]:
    game.hit(game.player)
    return (
        None,
        f"You got a {game.player[-1]}. Your hand value is now {game.get_hand_value(game.player)}",
    )


@engine.command
def flip(*_, game: BlackJack) -> tuple[GAME_RESULT, str]:
    result = game.flip()
    return (
        result,
        f"You {result}!\nYour hand value is {game.get_hand_value(game.player)}\nThe dealers hand value is {game.get_hand_value(game.dealer)}",
    )


def main():
    deck = list(
        itertools.chain(create_deck(), create_deck(), create_deck(), create_deck())
    )
    random.shuffle(deck)

    game = BlackJack(deck)

    result = None
    game.dealer_hit()
    print(f"You hand is {game.player} = {game.get_hand_value(game.player)}")
    while result == None:
        user = input("? ")

        result = string_to_args(user)

        cmd, args, _ = engine.parse(result)

        result, message = cmd(*args, game=game)

        print(message)

        if game.get_hand_value(game.player) > 21:
            result = game.flip()
            print(
                f"You {result}\nYou have bust! You hand value is {game.get_hand_value(game.player)} \nhThe dealer's hand value is {game.get_hand_value(game.dealer)}"
            )


if __name__ == "__main__":
    main()
