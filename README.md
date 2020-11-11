# Third Project: Othello

Third Project for COMP 560: Artificial Intelligence at Bridgewater State University.<br>

This project aims to write a minimax computer player for the game of Othello.

## Othello

Othello is played on a square grid.  Two players, white and black, who take turns placing their tokens on the grid.
The goal of each player is to maximize its tokens.  If a player places a token that flanks another player’s tokens, 
the internal tokens swap colors.  This means that if white has a token placed, and black has one or more tokens in a 
line from white’s token, and white places a token in a vacant  square at the end of the line, all of black’s pieces 
between white’s two tokens become white.

Some important rules are:
* You can only place on empty squares
* You may only place a piece such that it swaps an opponent piece.  Thus you cannot place arbitrarily
* If you cannot place your piece, your turn is skipped
* If neither player can place, the game is over.  This usually (but not always) happens when the board is filled
* At end game, the player with the most pieces wins.  Tied games are possible


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Have Python Installed;
* Have Pytest Installed;

### Running the Project

Git Clone this repository:

```
git clone https://github.com/cmontrond/ai-othello.git
```

CD into the project folder:

```
cd ai-othello
```

Run the project:

```
python othello.py
```

Testing using Pytest:

```
python -m pytest tests
```

## References
* [How to Play Othello or Reversi](https://www.youtube.com/watch?v=Ol3Id7xYsY4)
* [An Analysis of Heuristics in Othello](https://courses.cs.washington.edu/courses/cse573/04au/Project/mini1/RUSSIA/Final_Paper.pdf)

## What Was Successfully Accomplished
* Two AIs, where both AIs use a “greedy strategy”.  In a greedy strategy, the AI will consider all moves and take the best one, but will not search deeper ✔
* Two AIs, where both AIs use minimax to a depth of 1 ✔
* Two AIs, where both AIs use minimax to a user-specified depth ✔
* Alpha-Beta pruning, allowing for deeper searches ✔
* A better evaluation heuristic ✔
* Pruning of previously seen board states ❌

## Built With

* [Python](https://www.python.org/) - The Programming Language

## Author

**Christopher Montrond da Veiga Fernandes** - [Contact](mailto:cmontronddaveigafern@student.bridgew.edu)<br>

## Instructor

**Dr. Michael Black** - [Contact](mailto:m1black@bridgew.edu)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
