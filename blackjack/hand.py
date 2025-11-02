"""Hand representation and scoring utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from .cards import Card


@dataclass
class Hand:
    """Represents a Blackjack hand."""

    cards: List[Card] = field(default_factory=list)

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def clear(self) -> None:
        self.cards.clear()

    def values(self) -> List[int]:
        """Return all possible hand totals, considering soft totals."""

        totals = [0]
        for card in self.cards:
            new_totals: List[int] = []
            for total in totals:
                for value in card.values():
                    new_totals.append(total + value)
            totals = new_totals
        unique_totals = sorted(set(totals))
        return unique_totals

    def best_value(self) -> int:
        """Return the highest hand total <= 21, or the smallest total if bust."""

        valid_totals = [total for total in self.values() if total <= 21]
        if valid_totals:
            return max(valid_totals)
        return min(self.values())

    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.best_value() == 21

    def is_bust(self) -> bool:
        return self.best_value() > 21

    def is_soft(self) -> bool:
        totals = self.values()
        return any(total <= 21 for total in totals) and max(totals) != min(totals)

    def __iter__(self) -> Iterable[Card]:
        return iter(self.cards)

    def __len__(self) -> int:
        return len(self.cards)

    def __str__(self) -> str:  # pragma: no cover - for display only
        cards_str = " ".join(str(card) for card in self.cards)
        return f"[{cards_str}]"
