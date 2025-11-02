"""Player configuration used by the Blackjack game."""

from __future__ import annotations

from dataclasses import dataclass

from .strategies import Strategy


@dataclass
class PlayerConfig:
    """Represents a player taking part in the game."""

    name: str
    strategy: Strategy
    bankroll: float = 100.0
    bet_amount: float = 10.0

    def __post_init__(self) -> None:
        if self.bet_amount <= 0:
            raise ValueError("bet_amount must be a positive number")
        if self.bankroll <= 0:
            raise ValueError("bankroll must be a positive number")

    def can_place_bet(self) -> bool:
        return self.bankroll >= self.bet_amount

    def adjust_bankroll(self, amount: float) -> None:
        self.bankroll += amount
