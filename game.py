import pygame
import sys
from othello import Othello
import random
import math
import time
from minimax import get_computer_move
import threading

# H for human, C for computer, R for random

PLAYER1 = "C"
PLAYER2 = "C"

DIFFICULTY = 4 # difficulty (1-8) will take longer with higher values
DIFFICULTY2 = DIFFICULTY

COMP_DELAY = 100 # min time for computer move, does not affect difficulty just for aesthetics

SCREEN_WIDTH = 504
SCREEN_HEIGHT = 504
x_off = y_off = math.ceil(SCREEN_WIDTH / 18)
SQ_SIZE = SCREEN_WIDTH / 9


def draw_squares(surface):
    # draw border
    border = pygame.Rect(0,0,x_off,SCREEN_HEIGHT)
    pygame.draw.rect(surface, (0,0,0), border)
    border = pygame.Rect(0,0,SCREEN_WIDTH,y_off)
    pygame.draw.rect(surface, (0,0,0), border)
    border = pygame.Rect(SCREEN_WIDTH - x_off, 0, x_off, SCREEN_HEIGHT)
    pygame.draw.rect(surface, (0,0,0), border)
    border = pygame.Rect(0, SCREEN_HEIGHT - y_off, SCREEN_WIDTH, y_off)
    pygame.draw.rect(surface, (0,0,0), border)

    # draw lines
    for i in range(1,8):
        x = x_off + i*SQ_SIZE
        pygame.draw.line(surface, (0,25,0), (x, y_off), (x, SCREEN_HEIGHT - y_off), 2)
    for j in range(1,8):
        y = y_off + j*SQ_SIZE
        pygame.draw.line(surface, (0,25,0), (x_off, y), (SCREEN_HEIGHT - x_off, y), 2) 

def init_rects(surface):
    rects = [[None for _ in range(8)] for _ in range(8)]
    for x, arr in enumerate(rects):
        for y, piece in enumerate(arr):
            rects[x][y] = pygame.Rect(x_off + x*SQ_SIZE, y_off + y*SQ_SIZE, SQ_SIZE, SQ_SIZE)
    return rects       

def draw_pieces(surface, env, rects):
    board = env.board
    for x, arr in enumerate(board):
        for y, p in enumerate(arr):
            if board[x][y] == env.black:
                pygame.draw.circle(surface, (0,25,0), rects[x][y].center, SQ_SIZE / 2 - 1)
            if board[x][y] == env.white:
                pygame.draw.circle(surface, (235,255,235), rects[x][y].center, SQ_SIZE / 2 - 1)

def draw_moves(surface, env, moves, rects):
    if not moves:
        return
    board = env.board
    for move in moves:
        rect = rects[move[0]][move[1]]
        s = pygame.Surface((SQ_SIZE,SQ_SIZE), pygame.SRCALPHA)
        s.fill((0,0,0,128))
        surface.blit(s, (rect.x,rect.y))
    pygame.display.update()

def update(surface, env, rects):
    surface.fill(pygame.Color(5,128,5)) 
    draw_squares(surface)
    draw_pieces(surface, env, rects)

def computer_move(env, difficulty, move_wrapper):
    move_wrapper[0] = get_computer_move(env, max_depth=difficulty)

def main():
    env = Othello()
    valid_moves = env.get_moves()

    pygame.init()

    surface = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),0,32)
    pygame.display.set_caption("Othello")

    font = pygame.font.SysFont("bauhaus93",60)

    surface.fill(pygame.Color(5,128,5))
    draw_squares(surface)
    rects = init_rects(surface)
    draw_pieces(surface, env, rects)

    pygame.display.update()

    game_over = False
    space_down = False

    t = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for x, arr in enumerate(rects):
                    for y, r in enumerate(arr):       
                        if r.collidepoint(pygame.mouse.get_pos()):
                            # print(valid_moves)
                            if env.turn == env.black and PLAYER1 == "H" or env.turn == env.white and PLAYER2 == "H":
                                if not valid_moves:
                                    env.make_move(None)
                                    valid_moves = env.get_moves()
                                elif (x,y) in valid_moves:
                                    env.make_move([x,y])
                                    valid_moves = env.get_moves()
                                    # print(env.turn)
                                    env.print_board()
                                update(surface, env, rects)
                                pygame.display.update()
            if event.type == pygame.KEYDOWN:
                if env.terminal() and event.key == pygame.K_RETURN:
                    env = Othello()
                    update(surface, env, rects)
                    valid_moves = env.get_moves()
                    pygame.display.update()
                    game_over = False
                if event.key == pygame.K_SPACE:
                    #draw_moves(surface, env, valid_moves, rects)
                    space_down = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    #update(surface, env, rects)
                    space_down = False
                

        if env.terminal():
            if not game_over:
                winScreen = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT), pygame.SRCALPHA)
                winScreen.fill((255,255,255,128))
                winner = env.get_winner()
                if winner == env.black:
                    text = font.render('black wins', True, (0,0,0,255))
                elif winner == env.white:
                    text = font.render('white wins', True, (0,0,0,255))
                else:
                    text = font.render('draw', True, (0,0,0,255))
                text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
                winScreen.blit(text, text_rect)
                surface.blit(winScreen, (0,0))
                game_over = True
                pygame.display.update()
            continue
        if env.turn == env.black and PLAYER1 == "C" or env.turn == env.white and PLAYER2 == "C":
            if not t:
                # print(env.turn)
                start = time.time()
                move_wrapper = [None]
                if env.turn == env.black:
                    t = threading.Thread(target=computer_move, args=(env, DIFFICULTY, move_wrapper), daemon=True)
                else:
                    t = threading.Thread(target=computer_move, args=(env, DIFFICULTY2, move_wrapper), daemon=True)
                t.start()
            elif not t.is_alive():
                move = move_wrapper[0]
                end = time.time()
                delTime = COMP_DELAY - (int)((end - start) * COMP_DELAY)
                pygame.time.delay(delTime)
                env.make_move(move)
                valid_moves = env.get_moves()
                env.print_board()
                t = None
        elif env.turn == env.black and PLAYER1 == "R" or env.turn == env.white and PLAYER2 == "R":
            # print(env.turn)
            if valid_moves:
                start = time.time()
                move = random.choice(valid_moves)
                env.make_move(move)
                end = time.time()
                delTime = COMP_DELAY - (int)((end - start) * COMP_DELAY)
                pygame.time.delay(delTime)
            else:
                env.make_move(None)
            valid_moves = env.get_moves()
            env.print_board()
            
        #draw_pieces(surface, env, rects)
        update(surface, env, rects)
        if space_down:
            draw_moves(surface, env, valid_moves, rects)

        pygame.display.update()


if __name__ == "__main__":
    main()
