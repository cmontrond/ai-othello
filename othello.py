import random


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
        if not self.end():
            return " ", score_x, score_o
        if score_x > score_o:
            return 1, score_x, score_o
        elif score_o > score_x:
            return -1, score_x, score_o
        elif score_x == score_o:
            return "-", score_x, score_o

    # swaps player
    def other_player(self, turn):
        return -turn

    # score gives a value to the board from the point of view of the player
    def score(self, player):
        winner, score_x, score_o = self.win()
        if winner == 1:
            return 10
        if winner == self.other_player(player):
            return -10
        if winner == "-":
            return -5
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
        for y in range(10):
            line = ""
            for x in range(10):
                if self.index(x, y) == 1:
                    line = line + "X"
                elif self.index(x, y) == -1:
                    line = line + "O"
                else:
                    line = line + "."
            print(line)
        print()

    # state is an end game if there are no empty places
    def end(self):
        return not 0 in self.state


def get_greedy_move(board, move_list, turn):
    # go through the moves and score them
    for i in range(len(move_list)):
        value = board.score(turn)
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
    return move


def get_min_max_move(board, move_list, turn):

    # go through all the moves to score them
    for i in range(len(move_list)):
        value = board.score(turn)
        # end game? don't go further, use the score
        if value != 0:
            move_list[i] = (value, move_list[i])
        else:
            # need to look at opponent
            # get a list of all countermoves
            countermoves = board.valid_moves(board.other_player(turn))
            if len(countermoves) > 0:
                # score them
                for j in range(len(countermoves)):
                    # put the score at front of move so I can sort
                    countermoves[j] = (board.score(turn), countermoves[j])
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
    return move  # cut off the score and just return move


# this plays a game between two players that will play completely randomly
def game():
    # make the starting board
    board = Board()
    # start with player 1
    turn = 1
    while True:
        # get the moves
        move_list = board.valid_moves(turn)
        # no moves, skip the turn
        if len(move_list) == 0:
            turn = -turn
            continue
        # pick a move totally at random
        i = random.randint(0, len(move_list) - 1)
        # make a new board
        board = board.copy()
        # make the move
        board.place(move_list[i][0], move_list[i][1], turn)
        # swap players
        turn = -turn
        # print
        board.print_board()
        # wait for user to press a key
        input()
        # game over? stop.
        if board.end():
            break
    print("Score is", board.evaluate())


# greedy player
# one who goes for the win
# if it can't win, play random
# it should select a set of moves with the best score, and choose one randomly from it
def greedy():
    # make the starting board
    board = Board()
    # start with player 1
    turn = 1
    while True:
        # get the moves
        move_list = board.valid_moves(turn)
        # no moves, skip the turn
        if len(move_list) == 0:
            turn = -turn
            continue
        # use greedy algorithm to choose a move
        move = get_greedy_move(board, move_list, turn)[1]
        # make a new board
        board = board.copy()
        # make the move
        board.place(move[0], move[1], turn)
        # swap players
        turn = -turn
        # print
        board.print_board()
        # wait for user to press a key
        # input()
        # game over? stop.
        if board.end():
            break
    # print("Score is", board.evaluate())
    winner, score_x, score_o = board.win()
    print("X score is", score_x)
    print("O score is", score_o)


# one depth minimax
# look at all my moves, then all opponents, no further
#  behavior?  go for the win.  if no win, will block opponent
def min_max():
    depth = int(input("Enter the search depth: "))

    if depth == 1:
        # make the starting board
        board = Board()
        # start with player 1
        turn = 1
        while True:
            # get the moves
            move_list = board.valid_moves(turn)
            # no moves, skip the turn
            if len(move_list) == 0:
                turn = -turn
                continue
            # use greedy algorithm to choose a move
            move = (
                get_min_max_move(board, move_list, turn)[1]
                if turn == 1
                else random.choice(move_list)
            )
            # make a new board
            board = board.copy()
            # make the move
            board.place(move[0], move[1], turn)
            # swap players
            turn = -turn
            # print
            board.print_board()
            # wait for user to press a key
            # input()
            # game over? stop.
            if board.end():
                break
        # print("Score is", board.evaluate())
        winner, score_x, score_o = board.win()
        print("X score is", score_x)
        print("O score is", score_o)
    else:
        print("Invalid depth!")


if __name__ == "__main__":
    # game()
    # greedy()
    min_max()
