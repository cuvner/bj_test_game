"""Strategy implementations for the Blackjack game."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

from .cards import Card
from .hand import Hand


@dataclass(frozen=True)
class RoundSnapshot:
    """Information available to a strategy when making a decision."""

    round_number: int
    hand: Hand
    dealer_upcard: Card
    allowed_actions: Tuple[str, ...]
    cards_remaining: int
    player_bankroll: float
    bet_amount: float


class Strategy(ABC):
    """Base class for all player strategies."""

    name: str = "Unnamed Strategy"

    def on_round_start(self, snapshot: RoundSnapshot) -> None:
        """Hook that runs at the start of a round.

        Strategies can override this method to reset internal state.
        The default implementation does nothing.
        """

    def on_round_end(self, snapshot: RoundSnapshot, outcome: str, payout: float) -> None:
        """Hook called once the round finishes for a player."""

    @abstractmethod
    def decide(self, snapshot: RoundSnapshot) -> str:
        """Return the action the strategy wants to take.

        Strategies must return one of the actions provided in
        ``snapshot.allowed_actions``.
        """


class DealerStrategy(Strategy):
    """A strategy that mimics the dealer rules (stand on 17+)."""

    name = "Dealer Rules"

    def decide(self, snapshot: RoundSnapshot) -> str:
        best = snapshot.hand.best_value()
        if best < 17:
            return "hit"
        return "stand"


class SimpleStrategy(Strategy):
    """A learner-friendly hit/stand strategy.

    The player hits under 16 and stands otherwise.
    """

    name = "Simple Hit 16"

    def decide(self, snapshot: RoundSnapshot) -> str:
        if snapshot.hand.best_value() < 16:
            return "hit"
        return "stand"


class ConsoleStrategy(Strategy):
    """Interactive strategy that asks the user via the console."""

    name = "Console Player"

    def decide(self, snapshot: RoundSnapshot) -> str:  # pragma: no cover - requires input
        while True:
            actions = ", ".join(snapshot.allowed_actions)
            response = input(
                f"Your hand {snapshot.hand} (total {snapshot.hand.best_value()})\n"
                f"Dealer showing {snapshot.dealer_upcard}\n"
                f"Choose action [{actions}]: "
            ).strip().lower()
            if response in snapshot.allowed_actions:
                return response
            print(f"Invalid action '{response}'. Please choose from: {actions}")
