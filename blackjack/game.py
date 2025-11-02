"""Blackjack game engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - used only for type hints
    from .strategies import Strategy

from .cards import Shoe
from .hand import Hand
from .players import PlayerConfig
from .strategies import RoundSnapshot


@dataclass
class GameResult:
    """Outcome of a single round for a player."""

    player_name: str
    outcome: str
    payout: float
    player_total: int
    dealer_total: int
    is_blackjack: bool


@dataclass
class _RoundPlayerState:
    config: PlayerConfig
    hand: Hand = field(default_factory=Hand)
    bet: float = 0.0


class BlackjackGame:
    """Orchestrates the flow of Blackjack rounds."""

    def __init__(
        self,
        players: List[PlayerConfig],
        *,
        decks: int = 6,
        dealer_hits_soft_17: bool = False,
    ) -> None:
        self.players = players
        self.dealer_hits_soft_17 = dealer_hits_soft_17
        self.shoe = Shoe(decks)
        self.round_number = 0

    def play_round(self, *, verbose: bool = False) -> List[GameResult]:
        """Play a single round of Blackjack and return the results."""

        self.round_number += 1
        dealer_hand = Hand()
        player_states: Dict[str, _RoundPlayerState] = {}
        results: List[GameResult] = []

        # Filter players who can afford the bet
        active_players: List[PlayerConfig] = []
        for player in self.players:
            if player.can_place_bet():
                active_players.append(player)
            else:
                results.append(
                    GameResult(
                        player_name=player.name,
                        outcome="skip",
                        payout=0.0,
                        player_total=0,
                        dealer_total=0,
                        is_blackjack=False,
                    )
                )
        if not active_players:
            return results

        # Initial deal: two cards to each player and two to dealer
        for player in active_players:
            player_states[player.name] = _RoundPlayerState(config=player, bet=player.bet_amount)

        for _ in range(2):
            for state in player_states.values():
                state.hand.add_card(self.shoe.draw())
            dealer_hand.add_card(self.shoe.draw())

        dealer_upcard = dealer_hand.cards[0]

        # Player turns
        for player in active_players:
            state = player_states[player.name]
            hand = state.hand
            bet = state.bet
            finished = False

            snapshot = RoundSnapshot(
                round_number=self.round_number,
                hand=hand,
                dealer_upcard=dealer_upcard,
                allowed_actions=("hit", "stand"),
                cards_remaining=self.shoe.cards_remaining(),
                player_bankroll=player.bankroll,
                bet_amount=bet,
            )
            player.strategy.on_round_start(snapshot)

            if verbose:
                print(f"{player.name} starting hand: {hand} (total {hand.best_value()})")

            if hand.is_blackjack():
                if verbose:
                    print(f"{player.name} has a natural blackjack!")
                state.bet = bet
                continue

            while not finished:
                allowed_actions = ["hit", "stand"]
                if len(hand) == 2 and player.bankroll >= bet * 2:
                    allowed_actions.append("double")
                snapshot = RoundSnapshot(
                    round_number=self.round_number,
                    hand=hand,
                    dealer_upcard=dealer_upcard,
                    allowed_actions=tuple(allowed_actions),
                    cards_remaining=self.shoe.cards_remaining(),
                    player_bankroll=player.bankroll,
                    bet_amount=bet,
                )
                decision = player.strategy.decide(snapshot)
                if decision not in allowed_actions:
                    raise ValueError(f"Strategy {player.strategy.name} returned invalid action '{decision}'")

                if decision == "hit":
                    card = self.shoe.draw()
                    hand.add_card(card)
                    if verbose:
                        print(f"{player.name} hits and receives {card}. Total: {hand.best_value()}")
                    if hand.is_bust():
                        finished = True
                elif decision == "double":
                    bet *= 2
                    card = self.shoe.draw()
                    hand.add_card(card)
                    if verbose:
                        print(f"{player.name} doubles and receives {card}. Total: {hand.best_value()}")
                    finished = True
                else:  # stand
                    if verbose:
                        print(f"{player.name} stands on {hand.best_value()}")
                    finished = True

                if hand.is_blackjack() or hand.is_bust():
                    finished = True

            state.bet = bet

        # Dealer plays out hand
        if verbose:
            print(f"Dealer shows {dealer_hand}")
        while self._dealer_should_hit(dealer_hand):
            card = self.shoe.draw()
            dealer_hand.add_card(card)
            if verbose:
                print(f"Dealer draws {card}. Total: {dealer_hand.best_value()}")

        dealer_total = dealer_hand.best_value()
        dealer_bust = dealer_total > 21

        # Resolve bets
        for player in active_players:
            state = player_states[player.name]
            hand = state.hand
            bet = state.bet
            player_total = hand.best_value()
            is_blackjack = hand.is_blackjack()

            if hand.is_bust():
                outcome = "lose"
                payout = -bet
            elif is_blackjack and not dealer_hand.is_blackjack():
                outcome = "blackjack"
                payout = bet * 1.5
            elif dealer_bust:
                outcome = "win"
                payout = bet
            else:
                dealer_blackjack = dealer_hand.is_blackjack()
                if dealer_blackjack and not is_blackjack:
                    outcome = "lose"
                    payout = -bet
                elif player_total > dealer_total:
                    outcome = "win"
                    payout = bet
                elif player_total < dealer_total:
                    outcome = "lose"
                    payout = -bet
                else:
                    outcome = "push"
                    payout = 0.0

            player.adjust_bankroll(payout)
            result = GameResult(
                player_name=player.name,
                outcome=outcome,
                payout=payout,
                player_total=player_total,
                dealer_total=dealer_total,
                is_blackjack=is_blackjack,
            )
            results.append(result)

            outcome_snapshot = RoundSnapshot(
                round_number=self.round_number,
                hand=hand,
                dealer_upcard=dealer_upcard,
                allowed_actions=tuple(),
                cards_remaining=self.shoe.cards_remaining(),
                player_bankroll=player.bankroll,
                bet_amount=bet,
            )
            player.strategy.on_round_end(outcome_snapshot, outcome, payout)

            if verbose:
                print(
                    f"{player.name} {outcome.upper()}! Player total: {player_total}, "
                    f"Dealer total: {dealer_total}. Bankroll now {player.bankroll:.2f}"
                )

        if verbose:
            print("")

        return results

    def _dealer_should_hit(self, hand: Hand) -> bool:
        best = hand.best_value()
        if best < 17:
            return True
        if best == 17 and hand.is_soft() and self.dealer_hits_soft_17:
            return True
        return False


def play_single_game(
    player_one: Tuple[str, "Strategy"],
    player_two: Tuple[str, "Strategy"],
    *,
    bet_amount: float = 10.0,
    bankroll: float = 100.0,
    decks: int = 6,
    dealer_hits_soft_17: bool = False,
    verbose: bool = False,
) -> Dict[str, int]:
    """Play a single game between two players and the dealer.

    Parameters
    ----------
    player_one, player_two:
        Tuples containing a player name and a strategy instance. The strategy
        controls how the player makes decisions during the round.
    bet_amount:
        Amount each player wagers for the hand (default 10.0).
    bankroll:
        Initial bankroll for each player so they can place the bet (default 100.0).
    decks:
        Number of decks to load into the shoe (default 6).
    dealer_hits_soft_17:
        Whether the dealer should hit on a soft 17 (default False).
    verbose:
        If True, print the flow of the round to stdout.

    Returns
    -------
    Dict[str, int]
        Mapping of participant names to their final hand totals after the
        round. The returned dictionary always contains entries for each
        player and the bank (dealer).
    """

    name_one, strategy_one = player_one
    name_two, strategy_two = player_two

    players = [
        PlayerConfig(name=name_one, strategy=strategy_one, bankroll=bankroll, bet_amount=bet_amount),
        PlayerConfig(name=name_two, strategy=strategy_two, bankroll=bankroll, bet_amount=bet_amount),
    ]

    game = BlackjackGame(players, decks=decks, dealer_hits_soft_17=dealer_hits_soft_17)
    results = game.play_round(verbose=verbose)

    if not results:
        return {name_one: 0, name_two: 0, "Dealer": 0}

    totals: Dict[str, int] = {}
    dealer_total: int = results[0].dealer_total
    for result in results:
        totals[result.player_name] = result.player_total
        dealer_total = result.dealer_total

    if name_one not in totals:
        totals[name_one] = 0
    if name_two not in totals:
        totals[name_two] = 0

    totals["Bank"] = dealer_total
    return totals
