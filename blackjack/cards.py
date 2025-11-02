"""Card and deck utilities for the Blackjack game."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Sequence

SUITS: Sequence[str] = ("♠", "♥", "♦", "♣")
RANKS: Sequence[str] = (
    "A",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "J",
    "Q",
    "K",
)


@dataclass(frozen=True)
class Card:
    """Represents a single playing card."""

    rank: str
    suit: str

    def values(self) -> List[int]:
        """Return the numeric values of the card.

        Aces count as either 1 or 11, picture cards count as 10,
        and all other cards equal their pip value.
        """

        if self.rank == "A":
            return [1, 11]
        if self.rank in {"J", "Q", "K"}:
            return [10]
        return [int(self.rank)]

    def __str__(self) -> str:  # pragma: no cover - convenience for display
        return f"{self.rank}{self.suit}"


class Deck:
    """A standard 52-card deck."""

    def __init__(self, *, rng: random.Random | None = None) -> None:
        self._cards: List[Card] = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self._rng = rng or random.Random()
        self.shuffle()

    def shuffle(self) -> None:
        """Shuffle the deck in-place."""

        self._rng.shuffle(self._cards)

    def draw(self) -> Card:
        """Draw a card from the top of the deck."""

        if not self._cards:
            raise IndexError("Cannot draw from an empty deck")
        return self._cards.pop()

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self) -> Iterable[Card]:
        return iter(self._cards)


class Shoe:
    """A shoe is made up of multiple decks combined."""

    def __init__(self, decks: int = 6, *, rng: random.Random | None = None) -> None:
        if decks < 1:
            raise ValueError("A shoe must contain at least one deck")
        self.decks = decks
        self._rng = rng or random.Random()
        self._cards: List[Card] = []
        self._reshuffle()

    def _reshuffle(self) -> None:
        self._cards = [Card(rank, suit) for _ in range(self.decks) for suit in SUITS for rank in RANKS]
        self._rng.shuffle(self._cards)

    def draw(self) -> Card:
        if not self._cards:
            self._reshuffle()
        return self._cards.pop()

    def cards_remaining(self) -> int:
        return len(self._cards)
