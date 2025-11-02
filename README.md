# Blackjack Strategy Simulator

This project provides a console-based Blackjack engine aimed at GCSE/Year 10
students. It offers a clean Python API that lets you plug in different
strategies and pit them against each other without needing a graphical user
interface.

## Features

* Fully modelled game engine with cards, hands, players, and a dealer.
* Extensible strategy system – create your own strategy by subclassing
  `blackjack.strategies.Strategy`.
* Command-line simulation tool for running multiple rounds and comparing final
  bankrolls.
* Simple built-in strategies (`SimpleStrategy`, `DealerStrategy`, and
  `ConsoleStrategy`) to help you get started quickly.

## Getting Started

Create a virtual environment and install the project if you want to reuse it in
other projects. For a quick start you can simply run the simulation script
directly.

```bash
python simulate.py --rounds 20 --verbose
```

By default, two players are configured:

* **Simple** – hits until reaching 16 or more
* **Dealer** – plays using the dealer rules (stands on 17 or more)

At the end of the simulation the script prints each player's final bankroll.

## Customising Players and Strategies

You can define players on the command-line using the `--player` option. The
format is `name:strategy[:bankroll][:bet]` and the flag can be repeated.

```bash
python simulate.py --rounds 50 \
    --player Alice:simple:150:5 \
    --player Bob:dealer:200:10
```

Available strategy keys:

* `simple` – hits under 16, stands otherwise.
* `dealer` – plays like the dealer.
* `console` – asks the user for each decision via the console (great for
  teaching the game flow!).

If you do not define any players the script will use the two default players
mentioned above.

## Playing a Single Game Programmatically

For quick experiments you can play a single round between two named players by
using the helper function `blackjack.play_single_game`. Pass each player's name
and strategy instance, and the function will return the final hand totals for
the players and the dealer.

```python
from blackjack import play_single_game
from blackjack.strategies import DealerStrategy, SimpleStrategy

totals = play_single_game(("Alice", SimpleStrategy()), ("Bob", DealerStrategy()))
print(totals)
# Example output: {'Alice': 19, 'Bob': 21, 'Dealer': 20}
```

You can override the bet amount, bankroll, number of decks, and whether the
dealer hits on soft 17 using keyword arguments.

## Writing Your Own Strategy

Strategies live in `blackjack/strategies.py`. To create your own, subclass
`Strategy` and implement the `decide` method. The method receives a
`RoundSnapshot` with the current hand, dealer's up-card, the allowed actions,
and useful context such as the current round number and cards remaining in the
shoe.

```python
from blackjack.strategies import Strategy, RoundSnapshot


class StandOn18Strategy(Strategy):
    name = "Stand on 18"

    def decide(self, snapshot: RoundSnapshot) -> str:
        return "stand" if snapshot.hand.best_value() >= 18 else "hit"
```

You can then wire it up in `simulate.py` (add it to the `STRATEGIES` dictionary)
or create your own script to experiment with more advanced behaviour.

## Next Steps

This code base is intentionally compact so that students can explore and
experiment. Possible extensions include splitting pairs, implementing card
counting strategies, or collecting statistics across thousands of rounds.

Have fun exploring Blackjack strategies!
