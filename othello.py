import random
from enum import Enum


class AI(Enum):
    RANDOM = 1
    GREEDY = 2
    MINIMAX = 3


class Optimization(Enum):
    ALPHA_BETA = 1  # Alpha-Beta pruning, allowing for deeper searches
    HEURISTIC = 2  # A better evaluation heuristic
    PRUNING = 3  # Pruning of previously seen board states


# this class stores an othello board state
# the state is handled as a 1d list that stores a 10x10 board.  1 and -1 are the two colors, 0 are empty squares
class Board:
    # make a starting board.  There are four pieces in the center
    def __init__(self):
        self.state = [0] * 100
        self.state[44] = 1
        self.state[45] = -1
        self.state[54] = -1
        self.state[55] = 1

    # returns the score as the difference between the number of 1s and the number of -1s
    def evaluate(self) -> int:
        value = 0
        for i in range(100):
            if self.state[i] == 1:
                value = value + 1
            elif self.state[i] == -1:
                value = value - 1
        return value

    # win return 1,-1, ' ' (game isn't over), or '-' for tie. it also returns the score
    def win(self):
        score_x = 0
        score_o = 0
        for i in range(100):
            if self.state[i] == 1:
                score_x += 1
            elif self.state[i] == -1:
                score_o += 1
        # if not self.end():
        #     return " ", score_x, score_x, score_o
        if score_x > score_o:
            return 1, score_x, score_x, score_o
        if score_o > score_x:
            return -1, score_o, score_x, score_o
        if score_x == score_o:
            return "-", score_x, score_x, score_o

    def calculate_score(self, player):
        score = 0
        for i in range(100):
            if self.state[i] == player:
                score += 1
        return score

    # swaps player
    def other_player(self, turn):
        return -turn

    # score gives a value to the board from the point of view of the player
    def score(self, player):
        winner, winner_score, score_x, score_o = self.win()
        if winner == player:
            return winner_score * 10
        if winner == self.other_player(player):
            return winner_score * -10
        if winner == "-":
            return winner_score * -5
        # game ongoing? score 0
        return 0

    # returns a new board that is a copy of the current board
    def copy(self):
        board = Board()
        for i in range(100):
            board.state[i] = self.state[i]
        return board

    # given a x,y position, returns the tile within the 1d list
    def index(self, x, y) -> int:
        if 0 <= x < 10 and 0 <= y < 10:
            return self.state[x + y * 10]
        else:
            # out of bounds, return -2 for error
            return -2

    # given an x,y coordinate, and an id of 1 or -1, returns true if this is a valid move
    def can_place(self, x, y, id) -> bool:
        # square is not empty? return false
        if self.index(x, y) != 0:
            return False
        # these functions compute the 8 different directions
        dirs = [
            (lambda x: x, lambda y: y - 1),
            (lambda x: x, lambda y: y + 1),
            (lambda x: x - 1, lambda y: y - 1),
            (lambda x: x - 1, lambda y: y),
            (lambda x: x - 1, lambda y: y + 1),
            (lambda x: x + 1, lambda y: y - 1),
            (lambda x: x + 1, lambda y: y),
            (lambda x: x + 1, lambda y: y + 1),
        ]
        # for each direction...
        for xop, yop in dirs:
            # move one space.  is the piece the opponent's color?
            i, j = xop(x), yop(y)
            if self.index(i, j) != -id:
                # no, then we'll move on to the next direction
                continue
            # keep going until we hit our own piece
            i, j = xop(i), yop(j)
            while self.index(i, j) == -id:
                i, j = xop(i), yop(j)
            # if we found a piece of our own color, then this is a valid move
            if self.index(i, j) == id:
                return True
        return False  # if I can't capture in any direction, I can't place here

    # given an x,y coordinate, and an id of 1 or -1, place a tile (if valid) at x,y, and modify the state accordingly
    def place(self, x, y, id):
        # don't bother if it isn't a valid move
        if not self.can_place(x, y, id):
            return
        # place your piece at x,y
        self.state[x + y * 10] = id
        dirs = [
            (lambda x: x, lambda y: y - 1),
            (lambda x: x, lambda y: y + 1),
            (lambda x: x - 1, lambda y: y - 1),
            (lambda x: x - 1, lambda y: y),
            (lambda x: x - 1, lambda y: y + 1),
            (lambda x: x + 1, lambda y: y - 1),
            (lambda x: x + 1, lambda y: y),
            (lambda x: x + 1, lambda y: y + 1),
        ]
        # go through each direction
        for xop, yop in dirs:
            i, j = xop(x), yop(y)
            # move one space.  is the piece the opponent's color?
            if self.index(i, j) != -id:
                # no, then we can't capture in this direction.  we'll move on to the next one
                continue
            # keep going until we hit our own piece
            while self.index(i, j) == -id:
                i, j = xop(i), yop(j)
            # if we found a piece of our own color, then this is a valid move
            if self.index(i, j) == id:
                k, l = xop(x), yop(y)
                # go back and flip all the pieces to my color
                while k != i or l != j:
                    self.state[k + l * 10] = id
                    k, l = xop(k), yop(l)

    # returns a list of all valid x,y moves for a given id
    def valid_moves(self, id) -> list:
        moves = []
        for x in range(10):
            for y in range(10):
                if self.can_place(x, y, id):
                    moves = moves + [(x, y)]
        return moves

    # print out the board.  1 is X, -1 is O
    def print_board(self):
        print("  0123456789")
        for y in range(10):
            line = ""
            for x in range(10):
                if self.index(x, y) == 1:
                    line = line + "X"
                elif self.index(x, y) == -1:
                    line = line + "O"
                else:
                    line = line + "."
            print(y, line)
        print()
        # print(self.state)
        # print()

    def print_coordinate(self, coord_x, coord_y):
        for y in range(10):
            line = ""
            for x in range(10):
                if self.index(x, y) == 1:
                    line = line + "X"
                elif self.index(x, y) == -1:
                    line = line + "O"
                elif x == coord_x and y == coord_y:
                    line = line + "C"
                else:
                    line = line + "."
            print(line)
        print()

    # state is an end game if there are no empty places
    def end(self):
        if len(self.valid_moves(1)) == 0 and len(self.valid_moves(-1)) == 0:
            return True
        return not 0 in self.state


# greedy player
# one who goes for the win
# if it can't win, play random
# it should select a set of moves with the best score, and choose one randomly from it
def get_greedy_move(board, move_list, turn):
    # go through the moves and score them
    for i in range(len(move_list)):
        board_with_move = board.copy()
        board_with_move.place(move_list[i][0], move_list[i][1], turn)
        value = board_with_move.calculate_score(turn)
        # put the score as a tuple in front of the move
        move_list[i] = (value, move_list[i])

    # now I can sort them, biggest value first
    move_list.sort(reverse=True)

    # get a sublist of all the moves that are best
    index = 0
    top_score = move_list[0][0]
    while index < len(move_list) and move_list[index][0] == top_score:
        index += 1
    move_list = move_list[:index]

    # move_list now contains only my best moves (however many there are)
    # pick one randomly and return
    move = move_list[random.randrange(0, len(move_list))]
    return move[1]


# one depth minimax
# look at all my moves, then all opponents, no further
#  behavior?  go for the win.  if no win, will block opponent
def get_mini_max_move(board, depth, move_list, turn):
    # go through all the moves to score them
    for i in range(len(move_list)):
        board_with_move = board.copy()
        board_with_move.place(move_list[i][0], move_list[i][1], turn)
        value = board_with_move.calculate_score(turn)
        # end game? don't go further, use the score
        if board_with_move.end():
            move_list[i] = (value, move_list[i])
        else:
            # need to look at opponent
            # get a list of all countermoves
            countermoves = board.valid_moves(board.other_player(turn))
            if len(countermoves) > 0:
                # score them
                for j in range(len(countermoves)):
                    # put the score at front of move so I can sort
                    board_with_move = board.copy()
                    board_with_move.place(
                        countermoves[j][0], countermoves[j][1], board.other_player(turn)
                    )
                    countermoves[j] = (
                        # board.calculate_score(board.other_player(turn)),
                        board.calculate_score(turn),
                        countermoves[j],
                    )
                # rank them: but this time with the min first
                countermoves.sort(reverse=False)
                # get the score of the lowest move
                worst_score = countermoves[0][0]
                # now use that score to value my move
                move_list[i] = (worst_score, move_list[i])

    # now pick the best of the worst
    move_list.sort(reverse=True)
    # get a sublist of all the moves that are best
    index = 0
    top_score = move_list[0][0]
    while index < len(move_list) and move_list[index][0] == top_score:
        index = index + 1
    move_list = move_list[:index]
    # moves now contains only my best moves (however many there are)
    # pick one randomly and return
    move = move_list[random.randrange(0, len(move_list))]
    return move[1]  # cut off the score and just return move


def run_game(ai_type: AI):
    # if ai type in minimax, ask the user for the depth
    depth = 1
    if ai_type == AI.MINIMAX:
        depth = int(input("Enter the search depth: "))

    # make the starting board
    board = Board()
    # start with player 1
    turn = 1
    while not board.end():
        # get the moves
        move_list = board.valid_moves(turn)
        # no moves, skip the turn
        if len(move_list) == 0:
            turn = -turn
            continue

        # select an algorithm, defaults to random
        move = random.choice(move_list)
        if ai_type == AI.GREEDY:
            move = get_greedy_move(board, move_list, turn)
        elif ai_type == AI.MINIMAX:
            move = get_mini_max_move(board, depth, move_list, turn)

        # make a new board
        board = board.copy()
        # make the move
        board.place(move[0], move[1], turn)
        print("\nTurn:", "X" if turn == 1 else "O")
        # swap players
        turn = -turn
        # print
        board.print_board()
        # print("Board State:", board.state)
        # wait for user to press a key
        # input()
    # print("Score is", board.evaluate())
    winner, winner_score, score_x, score_o = board.win()
    print("X score is", score_x)
    print("O score is", score_o)


def dummy():
    board = Board()
    # board.print_coordinate(9, 9)

    # board.place(4, 6, 1)
    # board.place(3, 4, -1)

    board.state = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -1,
        0,
        1,
        -1,
        0,
        0,
        0,
        0,
        0,
        0,
        -1,
        1,
        -1,
        -1,
        -1,
        0,
        0,
        0,
        0,
        0,
        0,
        -1,
        1,
        -1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -1,
        -1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]

    board.print_board()
    print()

    starting_score = board.calculate_score(1)
    print("Starting Score", starting_score)
    print()

    print("Total moves", len(board.valid_moves(1)), end="\n\n")
    count = 1
    for coord in board.valid_moves(1):
        print("Move", count)
        test_board = board.copy()
        test_board.place(coord[0], coord[1], 1)
        # board.print_coordinate(coord[0], coord[1])
        score = test_board.calculate_score(1)
        test_board.print_board()
        print()
        print("Move:", coord)
        print("Score", score)
        print("Score Difference", score - starting_score)
        print()
        count += 1

    best_move = get_greedy_move(board, board.valid_moves(1), 1)

    print()
    print("BEST MOVE >>", best_move)  ## (4, 9)


def fix_mini_max():
    board = Board()

    board.state = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]

    print(board.valid_moves(-1))


if __name__ == "__main__":
    # game()
    # greedy()
    # min_max()
    run_game(AI.MINIMAX)
    # dummy()
    # fix_mini_max()
