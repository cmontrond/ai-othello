import random
from enum import Enum

mini_max_count = 0


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

    # Calculates the score for a specific player
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
    # this one actually calculates the difference between the player and the opponent
    def score(self, player):
        player_score = self.calculate_score(player)
        other_player_score = self.calculate_score(self.other_player(player))
        return player_score - other_player_score

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

    def valid_moves_mini_max(self, id, maximizing=True) -> list:
        moves = []
        for x in range(10):
            for y in range(10):
                if self.can_place(x, y, id):
                    if maximizing:
                        moves = moves + [(None, (x, y))]
                    else:
                        moves = moves + [(None, (x, y))]
        return moves

    # returns valid moves with associated scores
    def scored_valid_moves(self, id, score_for=1):
        moves = self.valid_moves(id)
        for i, move in enumerate(moves):
            board = self.copy()
            board.place(move[0], move[1], id)
            moves[i] = (board.score(score_for), move)
        return moves

    # difference in coins between the max player and min player.
    def heuristic_coin_parity(self, player):
        player_score = self.calculate_score(player)
        opponent_score = self.calculate_score(self.other_player(player))
        return 100 * (player_score - opponent_score) / (player_score + opponent_score)

    # number of next moves a player has, given the current state of the game
    def heuristic_mobility(self, player):
        player_mobility = len(self.valid_moves(player))
        opponent_mobility = len(self.valid_moves(self.other_player(player)))

        if player_mobility + opponent_mobility != 0:
            return (
                100
                * (player_mobility - opponent_mobility)
                / (player_mobility + opponent_mobility)
            )
        else:
            return 0

    # sums up the different heuristic functions
    def calculate_heuristic(self, player):
        return self.heuristic_coin_parity(player) + self.heuristic_mobility(player)

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
def get_greedy_move(original_board, move_list, turn):
    # go through the moves and score them
    for i in range(len(move_list)):
        board = original_board.copy()
        board.place(move_list[i][0], move_list[i][1], turn)
        value = board.score(turn)
        # put the score as a tuple in front of the move
        move_list[i] = (value, move_list[i])

    # now I can sort them, biggest value first
    move_list.sort(reverse=True, key=lambda x: x[0])

    # get a sublist of all the moves that are best
    index = 0
    top_score = move_list[0][0]
    while index < len(move_list) and move_list[index][0] == top_score:
        index += 1
    move_list = move_list[:index]

    # move_list now contains only my best moves (however many there are)
    # pick one randomly and return
    move = move_list[random.randrange(0, len(move_list))]
    if turn == 1:
        print("X's minimax moves:", move_list)
    return move[1]


# one depth minimax
# look at all my moves, then all opponents
#  behavior?  go for the win.  if no win, will block opponent
def get_mini_max_move_one_depth(original_board, move_list, turn):
    # go through all the moves to score them
    for i in range(len(move_list)):
        board = original_board.copy()
        board.place(move_list[i][0], move_list[i][1], turn)
        value = board.score(turn)
        # end game? don't go further, use the score
        if board.end():
            move_list[i] = (value, move_list[i])
        else:
            # need to look at opponent
            # get a list of all countermoves
            countermoves = board.valid_moves(board.other_player(turn))
            if len(countermoves) > 0:
                # score them
                for j in range(len(countermoves)):
                    # put the score at front of move so I can sort
                    new_board = board.copy()
                    new_board.place(
                        countermoves[j][0],
                        countermoves[j][1],
                        new_board.other_player(turn),
                    )
                    countermoves[j] = (
                        new_board.score(turn),
                        countermoves[j],
                    )
                # rank them: but this time with the min first
                countermoves.sort(reverse=False, key=lambda x: x[0])
                # get the score of the lowest move
                worst_score = countermoves[0][0]
                # now use that score to value my move
                move_list[i] = (worst_score, move_list[i])

    # now pick the best of the worst
    move_list.sort(reverse=True, key=lambda x: x[0])
    # get a sublist of all the moves that are best
    index = 0
    top_score = move_list[0][0]
    while index < len(move_list) and move_list[index][0] == top_score:
        index = index + 1
    move_list = move_list[:index]
    # moves now contains only my best moves (however many there are)
    # pick one randomly and return
    move = move_list[random.randrange(0, len(move_list))]
    if turn == 1:
        print("X's minimax moves:", move_list)
    return move[1]  # cut off the score and just return move


def get_mini_max_move_n_depth(
    original_board, move_list, turn, depth=-1, top_level=True
):
    # go through all the moves to score them
    for i in range(len(move_list)):
        # TODO: check if second position of move is a tuple, if so, the move is the second element
        # TODO: Else, do as you were doing before
        board = original_board.copy()
        board.place(move_list[i][0], move_list[i][1], turn)
        value = board.score(turn)
        # end game? don't go further, use the score
        if board.end():
            move_list[i] = (value, move_list[i])
        else:
            # need to look at opponent
            # get a list of all countermoves
            countermoves = board.valid_moves(board.other_player(turn))
            if len(countermoves) > 0:
                # score them
                for j in range(len(countermoves)):
                    # put the score at front of move so I can sort
                    new_board = board.copy()
                    new_board.place(
                        countermoves[j][0],
                        countermoves[j][1],
                        new_board.other_player(turn),
                    )
                    value = new_board.score(turn)
                    # TODO: Here is where you should call the same function recursively...?
                    # TODO: Have a global variable that you use to track how many times the function was called
                    # TODO: This way, you can see if the depth is working
                    if new_board.end():
                        countermoves[j] = (value, countermoves[j])
                    elif depth == 1:
                        countermoves[j] = (value, countermoves[j])
                    else:
                        value = get_mini_max_move_n_depth(
                            new_board,
                            new_board.valid_moves(turn),
                            turn,
                            depth=depth - 1,
                            top_level=False,
                        )
                        countermoves[j] = (value, countermoves[j])

                # rank them: but this time with the min first
                countermoves.sort(reverse=False, key=lambda x: x[0])
                # get the score of the lowest move
                worst_score = countermoves[0][0]
                # now use that score to value my move
                move_list[i] = (worst_score, move_list[i])
                # print(
                #     "X's move",
                #     move_list[i][1],
                #     "counter moves are",
                #     [cm[1] for cm in countermoves],
                # )

    # now pick the best of the worst
    move_list.sort(reverse=True, key=lambda x: x[0])

    if not top_level:
        return move_list[0][0]

    # get a sublist of all the moves that are best
    index = 0
    top_score = move_list[0][0]
    while index < len(move_list) and move_list[index][0] == top_score:
        index = index + 1
    move_list = move_list[:index]

    # moves now contains only my best moves (however many there are)
    # pick one randomly and return
    move = move_list[random.randrange(0, len(move_list))]

    if turn == 1:
        print("X's minimax moves:", move_list)
    return move[1]  # cut off the score and just return move


def get_mini_max_move_n_depth_pruning(
    original_board, turn, depth=-1, top_level=True, alpha=-10000, beta=10000
):
    move_list = original_board.valid_moves(turn)
    # go through all the moves to score them
    for i in range(len(move_list)):
        board = original_board.copy()
        board.place(move_list[i][0], move_list[i][1], turn)
        value = board.score(turn)
        # end game? don't go further, use the score
        if board.end():
            move_list[i] = (value, move_list[i])
        else:
            alpha = max([alpha, value])

            if beta <= alpha:
                move_list[i] = (alpha, move_list[i])
                # move_list = move_list[: i + 1]
                break

            # need to look at opponent
            # get a list of all countermoves
            countermoves = board.valid_moves(board.other_player(turn))
            if len(countermoves) > 0:
                # score them
                for j in range(len(countermoves)):
                    # put the score at front of move so I can sort
                    new_board = board.copy()
                    new_board.place(
                        countermoves[j][0],
                        countermoves[j][1],
                        new_board.other_player(turn),
                    )
                    value = new_board.score(turn)
                    if new_board.end():
                        countermoves[j] = (value, countermoves[j])
                    elif depth == 1:
                        countermoves[j] = (value, countermoves[j])
                    else:
                        helper = len(new_board.valid_moves(turn))
                        if helper > 0:
                            value = get_mini_max_move_n_depth_pruning(
                                new_board,
                                turn,
                                depth=depth - 1,
                                top_level=False,
                                alpha=alpha,
                                beta=beta,
                            )
                            countermoves[j] = (value, countermoves[j])
                        else:
                            countermoves[j] = (value, countermoves[j])

                    beta = min([beta, value])
                    if beta <= alpha:
                        move_list[i] = (beta, move_list[i])
                        # move_list = move_list[: i + 1]
                        break

                # rank them: but this time with the min first
                countermoves.sort(reverse=False, key=lambda x: x[0])
                # get the score of the lowest move
                worst_score = countermoves[0][0]

                # now use that score to value my move
                if type(move_list[i][1]) == tuple:
                    move_list[i] = (worst_score, move_list[i][1])
                else:
                    move_list[i] = (worst_score, move_list[i])
                # print(
                #     "X's move",
                #     move_list[i][1],
                #     "counter moves are",
                #     [cm[1] for cm in countermoves],
                # )
            else:
                move_list[i] = (value, move_list[i])

    # now pick the best of the worst
    move_list = [(m[0], m[1]) for m in move_list if (type(m[1]) == tuple)]

    move_list.sort(reverse=True, key=lambda x: x[0])

    if not top_level:
        return move_list[0][0]

    # get a sublist of all the moves that are best
    index = 0
    top_score = move_list[0][0]
    while index < len(move_list) and move_list[index][0] == top_score:
        index = index + 1
    move_list = move_list[:index]

    # moves now contains only my best moves (however many there are)
    # pick one randomly and return
    move = move_list[random.randrange(0, len(move_list))]

    # if turn == 1:
    #     print("X's minimax moves:", move_list)
    return move[1]  # cut off the score and just return move


# here, we actually implement an heuristic to improve our minimax algorithm
def get_mini_max_move_n_depth_pruning_heuristic(
    original_board, turn, depth=-1, top_level=True, alpha=-10000, beta=10000
):
    move_list = original_board.valid_moves(turn)
    # go through all the moves to score them
    for i in range(len(move_list)):
        board = original_board.copy()
        board.place(move_list[i][0], move_list[i][1], turn)
        value = board.score(turn)
        # end game? don't go further, use the score
        if board.end():
            move_list[i] = (value, move_list[i])
        else:
            alpha = max([alpha, value])

            if beta <= alpha:
                move_list[i] = (alpha, move_list[i])
                # move_list = move_list[: i + 1]
                break

            # need to look at opponent
            # get a list of all countermoves
            countermoves = board.valid_moves(board.other_player(turn))
            if len(countermoves) > 0:
                # score them
                for j in range(len(countermoves)):
                    # put the score at front of move so I can sort
                    new_board = board.copy()
                    new_board.place(
                        countermoves[j][0],
                        countermoves[j][1],
                        new_board.other_player(turn),
                    )
                    value = new_board.score(turn)
                    if new_board.end():
                        countermoves[j] = (value, countermoves[j])
                    elif depth == 1:
                        countermoves[j] = (value, countermoves[j])
                    else:
                        helper = len(new_board.valid_moves(turn))
                        if helper > 0:
                            value = get_mini_max_move_n_depth_pruning_heuristic(
                                new_board,
                                turn,
                                depth=depth - 1,
                                top_level=False,
                                alpha=alpha,
                                beta=beta,
                            )
                            countermoves[j] = (value, countermoves[j])
                        else:
                            countermoves[j] = (value, countermoves[j])

                    beta = min([beta, value])
                    if beta <= alpha:
                        move_list[i] = (beta, move_list[i])
                        # move_list = move_list[: i + 1]
                        break

                # rank them: but this time with the min first
                countermoves.sort(reverse=False, key=lambda x: x[0])
                # get the score of the lowest move
                worst_score = countermoves[0][0]

                # now use that score to value my move
                if type(move_list[i][1]) == tuple:
                    move_list[i] = (worst_score, move_list[i][1])
                else:
                    move_list[i] = (worst_score, move_list[i])
            else:
                move_list[i] = (value, move_list[i])

    # now pick the best of the worst
    move_list = [(m[0], m[1]) for m in move_list if (type(m[1]) == tuple)]

    move_list.sort(reverse=True, key=lambda x: x[0])

    if not top_level:
        return move_list[0][0]

    # get a sublist of all the moves that are best
    index = 0
    top_score = move_list[0][0]
    while index < len(move_list) and move_list[index][0] == top_score:
        index = index + 1
    move_list = move_list[:index]

    # moves now contains only my best moves (however many there are)
    # pick one randomly and return
    move = move_list[random.randrange(0, len(move_list))]

    # if turn == 1:
    #     print("X's minimax moves:", move_list)
    return move[1]  # cut off the score and just return move


def get_human_move(movelist):
    choice = (-1, -1)

    while choice not in movelist:
        print("\nChoose one of the following moves:")
        print(movelist)
        user_input = input("\nChoice >> ")
        choice = (int(user_input.split()[0]), int(user_input.split()[1]))
        if choice not in movelist:
            print("\nInvalid move!")

    return choice


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
        1,
        1,
        -1,
        0,
        0,
        0,
        0,
        0,
        -1,
        -1,
        -1,
        -1,
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

    print("X's moves:", board.scored_valid_moves(1))
    # greedy_move = get_greedy_move(board, board.valid_moves(1), 1)
    # print("X's greedy move", greedy_move)

    # minimax_move = get_mini_max_move_one_depth(board, board.valid_moves(1), 1)
    minimax_move = get_mini_max_move_n_depth(
        board, board.valid_moves(1), turn=1, depth=2, top_level=True
    )
    print("\nX's minimax move", minimax_move)
    #
    # new_board = board.copy()
    # new_board.place(1, 5, 1)

    # print()
    # new_board.print_board()
    # print("\nO's scored moves for X's (1,5) move:", new_board.scored_valid_moves(-1))

    # new_board = board.copy()
    # new_board.place(8, 2, 1)

    # print()
    # new_board.print_board()
    # print("\nO's scored moves for X's (8,2) move:", new_board.scored_valid_moves(-1))

    # print("Minimax Count:", mini_max_count)


def run_game(user_inputs=False):
    # if ai type in minimax, ask the user for the depth
    depth = 1
    if user_inputs:
        depth = int(input("Enter the search depth: "))

    # make the starting board
    board = Board()
    # board.state = [
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     1,
    #     0,
    #     0,
    #     0,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     1,
    #     -1,
    #     0,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     1,
    #     -1,
    #     0,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     0,
    #     -1,
    #     1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     0,
    #     -1,
    #     1,
    #     1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     1,
    #     -1,
    #     0,
    #     -1,
    #     1,
    #     -1,
    #     1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     1,
    #     1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     0,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     0,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     0,
    #     0,
    # ]
    # board.state = [
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     1,
    #     -1,
    #     -1,
    #     1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     1,
    #     1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     1,
    #     1,
    #     -1,
    #     1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     -1,
    #     -1,
    #     -1,
    #     -1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     1,
    #     0,
    # ]
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
        if turn == 1:
            # move = random.choice(move_list)
            # move = get_greedy_move(board, move_list, turn)
            # move = get_mini_max_move_one_depth(board, move_list, turn)
            # move = get_mini_max_move_n_depth(board, move_list, turn, 2)
            move = get_mini_max_move_n_depth_pruning(board, turn, 3)
        else:
            # move = random.choice(move_list)
            # move = get_greedy_move(board, move_list, turn)
            # move = get_mini_max_move_one_depth(board, move_list, turn)
            # move = get_mini_max_move_n_depth(board, move_list, turn, 2)
            # move = get_human_move(move_list)
            move = get_mini_max_move_n_depth_pruning(board, turn, 1)

        # make a new board
        board = board.copy()
        # make the move
        board.place(move[0], move[1], turn)

        # print whose turn it is
        print("\nTurn:", "X" if turn == 1 else "O")

        # swap players
        turn = -turn
        # print
        board.print_board()

        # print("Board State:", board.state)

        # wait for user to press a key
        # input()

    score_x = board.calculate_score(1)
    score_o = board.calculate_score(-1)
    print("X score is", score_x)
    print("O score is", score_o)


if __name__ == "__main__":
    run_game()
    # fix_mini_max()
