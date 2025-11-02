"""Command-line interface for running Blackjack simulations."""

from __future__ import annotations

import argparse
from typing import Dict, List, Type

from blackjack.game import BlackjackGame
from blackjack.players import PlayerConfig
from blackjack.strategies import ConsoleStrategy, DealerStrategy, SimpleStrategy, Strategy

STRATEGIES: Dict[str, Type[Strategy]] = {
    "simple": SimpleStrategy,
    "dealer": DealerStrategy,
    "console": ConsoleStrategy,
}


def parse_player(definition: str) -> PlayerConfig:
    """Parse a player definition of the form ``name:strategy[:bankroll][:bet]``."""

    parts = definition.split(":")
    if len(parts) < 2:
        raise ValueError("Player definition must be in the format name:strategy[:bankroll][:bet]")

    name, strategy_key, *rest = parts
    strategy_class = STRATEGIES.get(strategy_key.lower())
    if strategy_class is None:
        known = ", ".join(sorted(STRATEGIES))
        raise ValueError(f"Unknown strategy '{strategy_key}'. Available: {known}")

    bankroll = float(rest[0]) if len(rest) >= 1 and rest[0] else 100.0
    bet_amount = float(rest[1]) if len(rest) >= 2 and rest[1] else 10.0
    strategy = strategy_class()
    return PlayerConfig(name=name, strategy=strategy, bankroll=bankroll, bet_amount=bet_amount)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a Blackjack simulation.")
    parser.add_argument("--rounds", type=int, default=10, help="Number of rounds to play (default: 10)")
    parser.add_argument("--decks", type=int, default=6, help="Number of decks in the shoe (default: 6)")
    parser.add_argument(
        "--dealer-soft-17",
        action="store_true",
        help="Dealer hits on soft 17 (default: stand on soft 17)",
    )
    parser.add_argument(
        "--player",
        action="append",
        help=(
            "Player definition in the format name:strategy[:bankroll][:bet]. "
            "Can be specified multiple times."
        ),
    )
    parser.add_argument("--verbose", action="store_true", help="Print the details of each round")
    args = parser.parse_args()

    players: List[PlayerConfig]
    if args.player:
        players = []
        for definition in args.player:
            try:
                players.append(parse_player(definition))
            except ValueError as exc:
                parser.error(str(exc))
    else:
        players = [
            PlayerConfig(name="Simple", strategy=SimpleStrategy(), bankroll=100.0, bet_amount=10.0),
            PlayerConfig(name="Dealer", strategy=DealerStrategy(), bankroll=100.0, bet_amount=10.0),
        ]

    game = BlackjackGame(players, decks=args.decks, dealer_hits_soft_17=args.dealer_soft_17)

    for _ in range(args.rounds):
        game.play_round(verbose=args.verbose)

    print("Final bankrolls:")
    for player in players:
        print(f"- {player.name}: {player.bankroll:.2f}")


if __name__ == "__main__":
    main()
