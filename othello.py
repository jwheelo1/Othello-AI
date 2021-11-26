import numpy as np
import time
import random

class Othello:
    def __init__(self):
        self.board = np.zeros((8,8), dtype=np.int16)
        self.black = 1
        self.white = -1
        self.add_piece(self.white, 3, 3)
        self.add_piece(self.white, 4, 4)
        self.add_piece(self.black, 3, 4)
        self.add_piece(self.black, 4, 3)
        self.turn = self.black
        self.blackpass = False
        self.whitepass = False

    def get_moves(self):
        moves = []
        for y, arr in enumerate(self.board):
            for x, p in enumerate(arr):
                if self.is_valid(x, y):
                    moves.append((x, y))
        if len(moves) == 0:
            return None
        if self.turn == self.black:
            self.blackpass = False
        elif self.turn == self.white:
            self.whitepass = False
        return moves
    
    def make_move(self, move):
        if not move:
            self.turn = self.get_opp()
            if self.turn == self.black:
                self.blackpass = True
            elif self.turn == self.white:
                self.whitepass = True
            return
        x = move[0]
        y = move[1]
        self.add_piece(self.get_turn(), x, y)

        # go in each direction until another of the same color is reached
        # if not, can't go in that direction
        # basically have a square around x, y that grows
        sq_dirs = np.array([[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]])
        sq_points = np.array([[x,y] for _ in range(8)])
        
        sq_points = sq_points + sq_dirs # move in each direction
        sq_flips = [[] for _ in range(8)]
        sq_valid = np.array([False for _ in range(8)])

        # if opponent in that direction
        for i, sq in enumerate(sq_points):
            if sq[0] < 0 or sq[1] < 0 or sq[0] >= 8 or sq[1] >= 8:
                continue
            if self.get_piece(sq[0], sq[1]) == self.get_opp():
                sq_flips[i].append(sq)
                sq_valid[i] = True

        while True:
            sq_points = sq_points + sq_dirs # move in each direction

            # if opponent in that direction
            for i, sq in enumerate(sq_points):
                if sq[0] < 0 or sq[1] < 0 or sq[0] >= 8 or sq[1] >= 8 or not sq_valid[i]:
                    sq_valid[i] = False
                    continue
                if self.get_piece(sq[0], sq[1]) == self.get_opp():
                    sq_flips[i].append(sq)
                elif self.get_piece(sq[0], sq[1]) == self.get_turn() and len(sq_flips) != 0:
                    
                    for sq2 in sq_flips[i]:
                        self.flip_piece(sq2[0], sq2[1])
                    sq_flips[i] = []
                    sq_valid[i] = False
                else:
                    sq_valid[i] = False
            if not np.any(sq_valid):
                break
        self.turn = self.get_opp()

    def is_valid(self, x, y):
        # go in each direction until another of the same color is reached
        # if not, can't go in that direction
        # basically have a square around x, y that grows
        if self.get_piece(x, y) != 0:
            return False
        
        sq_dirs = np.array([[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]])
        sq_points = np.array([[x,y] for _ in range(8)])
        
        sq_points = sq_points + sq_dirs # move in each direction
        sq_valid = np.array([False for _ in range(8)])

        #print(x,y)
        #print(sq_points)

        # if opponent in that direction
        for i, sq in enumerate(sq_points):
            if sq[0] < 0 or sq[1] < 0 or sq[0] >= 8 or sq[1] >= 8:
                continue
            if self.get_piece(sq[0], sq[1]) == self.get_opp():
                sq_valid[i] = True

        if not np.any(sq_valid):
            return False

        while True:
            sq_points = sq_points + sq_dirs # move in each direction

            # if opponent in that direction
            for i, sq in enumerate(sq_points):
                if sq[0] < 0 or sq[1] < 0 or sq[0] >= 8 or sq[1] >= 8 or not sq_valid[i]:
                    sq_valid[i] = False
                    continue
                if self.get_piece(sq[0], sq[1]) == self.get_opp():
                    sq_valid[i] = True
                elif self.get_piece(sq[0], sq[1]) == self.get_turn() and sq_valid[i]:
                    return True
                else:
                    sq_valid[i] = False
            if not np.any(sq_valid):
                return False
            
        return False


    def print_board(self):
        print('+-----------------+')
        for x, arr in enumerate(self.board):
            string = '|'
            for y, p in enumerate(arr):
                if self.board[y][x] == 0:
                    string += '  '
                elif self.board[y][x] == self.black: 
                    string += ' ○'
                else:
                    string += ' ●'
            string += ' |'
            print(string)
        print('+-----------------+')

    def terminal(self):
        passes = self.blackpass and self.whitepass
        full = np.where(self.board == 0)[0].size == 0
        return passes or full

    def add_piece(self, p, x, y):
        self.board[x, y] = p

    def flip_piece(self, x, y):
        if self.get_piece(x, y) != 0:
            self.board[x, y] = self.get_turn()

    def get_piece(self, x, y):
        return self.board[x, y]
    
    def get_turn(self):
        return self.turn

    def get_num_black(self):
        return np.where(self.board == self.black)[0].size
    
    def get_num_white(self):
        return np.where(self.board == self.white)[0].size

    def get_winner(self):
        if not self.terminal():
            return 0
        else:
            num_black = self.get_num_black()
            num_white = self.get_num_white()
            if num_black > num_white:
                return self.black
            elif num_white > num_black:
                return self.white
            else:
                return 0
    
    def get_opp(self):
        return -self.turn



def main():
    env = Othello()
    while( not env.terminal() ):
        move = get_computer_move(env, 6)
        # moves = env.get_moves()
        # print(moves)
        # if moves:
        #     move = random.choice(moves)
        #     env.make_move(move[0], move[1])
        #     print(move)
        env.make_move(move)
        env.print_board()
    print(env.get_winner())

if __name__ == '__main__':
    main()

