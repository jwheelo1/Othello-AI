from othello import Othello
import copy
import numpy as np
import time


def get_computer_move(env, max_depth=4):
    NUM_STATES = [0, 0]
    start = time.time()
    value, move = MaxValue(env.turn, env, float('-inf'), float('inf'), 0, max_depth, NUM_STATES)
    end = time.time()
    print(f'num states examined: {NUM_STATES[0]:,d}; pruned ≈ {NUM_STATES[1]:,d}; depth: {max_depth}; max value: {value:,.0f}; seconds elapsed: {end - start:,.2f}')
    return move

def MaxValue(player, env, alpha, beta, depth, max_depth, num_states):
    num_states[0] += 1
    if env.get_winner() == player:
        return float('inf'), None
    elif env.get_winner() == -player:
        return float('-inf'), None
    if depth >= max_depth: # evaluate node with utility function if maxdepth reached
        return heuristic(player, env), None
    moves = env.get_moves()
    value = float('-inf')
    best_move = None
    if not moves:
        env2 = copy.deepcopy(env)
        env2.make_move(None)
        return MinValue(-player, env, alpha, beta, depth+1, max_depth, num_states)
    for move in moves:
        env2 = copy.deepcopy(env)
        env2.make_move(move)
        # find the move that the min player would pick
        value2, move2 =  MinValue(-player, env2, alpha, beta, depth + 1, max_depth, num_states)
        # if its better than the best so far, save it
        if value2 >= value:
            value = value2
            best_move = move
            alpha = max(alpha, value)
        # if pruning, prune what you can
        if value >= beta:
            num_states[1] += 10**(max_depth - depth)
            return value, best_move

    return value, best_move

    
def MinValue(player, env, alpha, beta, depth, max_depth, num_states):
    num_states[0] += 1
    if env.get_winner() == -player:
        return float('inf'), None
    elif env.get_winner() == player:
        return float('-inf'), None
    if depth >= max_depth: # evaluate node with utility function if maxdepth reached
        return heuristic(-player, env), None
    moves = env.get_moves()
    value = float('inf')
    best_move = None
    if not moves:
        env2 = copy.deepcopy(env)
        env2.make_move(None)
        return MaxValue(-player, env, alpha, beta, depth+1, max_depth, num_states)
    for move in moves:
        env2 = copy.deepcopy(env)
        env2.make_move(move)
        # find the move that max player would choose
        value2, move2 =  MaxValue(-player, env2, alpha, beta, depth + 1, max_depth, num_states)
        # if the move is lower than what has been found, save it
        if value2 < value:
            value = value2
            best_move = move
            beta = min(beta, value)
        # if pruning, prune
        if value <= alpha:
            num_states[1] += 10**(max_depth - depth)
            return value, best_move
    return value, best_move

def coin_parity(max_player, env):
    if max_player == env.black:
        max_coins = env.get_num_black()
        min_coins = env.get_num_white()
    else:
        max_coins = env.get_num_white()
        min_coins = env.get_num_black()
    return 100 * (max_coins - min_coins) / (max_coins + min_coins)

def mobility(max_player, env):
    env2 = copy.deepcopy(env)
    env2.turn = max_player
    max_moves = env2.get_moves()
    env2.turn = -max_player
    min_moves = env2.get_moves()
    if not max_moves and not min_moves:
        return 0
    if not max_moves:
        max_moves = []
    if not min_moves:
        min_moves = []
    return 100 * (len(max_moves) - len(min_moves)) / (len(max_moves) + len(min_moves))

def corners_captured(max_player, env):
    max_corners = 0
    min_corners = 0
    for corner in [[0,0],[7,0],[0,7],[7,7]]:
        if env.board[corner[0]][corner[1]] == max_player:
            max_corners += 1
        elif env.board[corner[0]][corner[1]] == -max_player:
            min_corners += 1
    return 25 * (max_corners - min_corners), max_corners, min_corners

def protection(env, piece, disc_dict):
    PROTECTED = 1
    UNPROTECTED = 0
    TAKEABLE = -1
    directions = [([-1,-1],[1,1]),([0,-1],[0,1]),([1,-1],[-1,1]),([-1,0],[1,0])]
    player = env.board[piece[0], piece[1]]
    for direction, value in enumerate(disc_dict[f'{piece}']):
        passed_through = []
        if value != None:
            continue
        reaches_border = [False, False]
        reaches_opp = [False, False]
        direction_l, direction_r = directions[direction]
        index = 1
        while not (direction_l == [0,0] and direction_r == [0,0]):
            piece_index_l = [piece[0] + index * direction_l[0], piece[1] + index * direction_l[1]]
            piece_index_r = [piece[0] + index * direction_r[0], piece[1] + index * direction_r[1]]
            if min(piece_index_l) < 0 or max(piece_index_l) > 7:
                reaches_border[0] = True
                direction_l = [0,0]
                piece_l = 0
            else:
                piece_l = env.board[piece_index_l[0], piece_index_l[1]]
            if min(piece_index_r) < 0 or max(piece_index_r) > 7:
                reaches_border[1] = True
                direction_r = [0,0]
                piece_r = 0
            else:
                piece_r = env.board[piece_index_r[0], piece_index_r[1]]
            if piece_l == -player:
                reaches_opp[0] = True
            if piece_r == -player:
                reaches_opp[1] = True
            if piece_l == 0:
                direction_l = [0,0]
            elif direction_l != [0,0]:
                passed_through.append(piece_index_l)
            if piece_r == 0:
                direction_r = [0,0]
            elif direction_r != [0,0]:
                passed_through.append(piece_index_r)
            index += 1
        if reaches_border[0] or reaches_border[1]:
            # print(f'protected1, {piece, direction, reaches_border}')
            disc_dict[f'{piece}'][direction] = PROTECTED
        elif reaches_opp[0] and reaches_opp[1]:
            # print(f'protected2, {piece, direction, reaches_opp}')
            disc_dict[f'{piece}'][direction] = PROTECTED
        elif reaches_opp[0] or reaches_opp[1]:
            disc_dict[f'{piece}'][direction] = TAKEABLE
        else:
            disc_dict[f'{piece}'][direction] = UNPROTECTED
        for piece2 in passed_through:
            if env.board[piece2[0], piece2[1]] == 0:
                continue
            if env.board[piece2[0], piece2[1]] == player:
                disc_dict[f'{piece2}'][direction] = disc_dict[f'{piece}'][direction]
            protection(env, piece2, disc_dict)

def corner_closeness(max_player, env):
    
    max_close = min_close = 0
    if env.board[0,0] == 0:
        if env.board[0,1] == max_player:
            max_close += 1
        elif env.board[0,1] == -max_player:
            min_close += 1 
        if env.board[1,0] == max_player:
            max_close += 1
        elif env.board[1,0] == -max_player:
            min_close += 1
        if env.board[1,1] == max_player:
            max_close += 1
        elif env.board[1,1] == -max_player:
            min_close += 1
    if env.board[0,7] == 0:
        if env.board[0,6] == max_player:
            max_close += 1
        elif env.board[0,6] == -max_player:
            min_close += 1 
        if env.board[1,7] == max_player:
            max_close += 1
        elif env.board[1,7] == -max_player:
            min_close += 1
        if env.board[1,6] == max_player:
            max_close += 1
        elif env.board[1,6] == -max_player:
            min_close += 1
    if env.board[7,0] == 0:
        if env.board[7,1] == max_player:
            max_close += 1
        elif env.board[7,1] == -max_player:
            min_close += 1 
        if env.board[6,0] == max_player:
            max_close += 1
        elif env.board[6,0] == -max_player:
            min_close += 1
        if env.board[6,1] == max_player:
            max_close += 1
        elif env.board[6,1] == -max_player:
            min_close += 1
    if env.board[7,7] == 0:
        if env.board[7,6] == max_player:
            max_close += 1
        elif env.board[7,6] == -max_player:
            min_close += 1 
        if env.board[6,7] == max_player:
            max_close += 1
        elif env.board[6,7] == -max_player:
            min_close += 1
        if env.board[6,6] == max_player:
            max_close += 1
        elif env.board[6,6] == -max_player:
            min_close += 1
    return 12.5 * (max_close - min_close)

def stability(player, env, max_c, min_c):
    PROTECTED = 1
    UNPROTECTED = 0
    TAKEABLE = -1
    #if max_c == 0 and min_c == 0:
    #    return 0, 0, 0, 0
    disc_dict = {}
    where = np.where(env.board != 0)
    discs = [[where[0][i], where[1][i]] for i in range(len(where[0]))]
    for disc in discs:
        disc_dict[f'{disc}'] = [None, None, None, None]
    protection(env, discs[0], disc_dict)

    num_stable_p = 0
    num_stable_o = 0
    num_danger_p = 0
    num_danger_o = 0
    num_unprot_p = 0
    num_unprot_o = 0
    for disc in discs:
        vals = np.array(disc_dict[f'{disc}'])
        if np.all(vals == PROTECTED):
            if env.board[disc[0], disc[1]] == player:
                num_stable_p += 1
            else:
                num_stable_o += 1
        elif np.any(vals == TAKEABLE):
            if env.board[disc[0], disc[1]] == player:
                num_danger_p += 1
            else:
                num_danger_o += 1
        else:
            if env.board[disc[0], disc[1]] == player:
                num_unprot_p += 1
            else:
                num_unprot_o += 1
    return num_stable_p, num_stable_o, num_danger_p, num_danger_o, num_unprot_p, num_unprot_o

def stability_heuristic(max_player, env, max_c, min_c):
    weight_stable = 1
    weight_danger = -1
    weight_unstable = -0.05
    s, s2, d, d2, u, u2 = stability(max_player, env, max_c, min_c)
    score_p = weight_stable*s + weight_danger*d + weight_unstable*u
    score_o = weight_stable*s2 + weight_danger*d2 + weight_unstable*u2
    if score_p + score_o != 0:
        return 100 * (score_p - score_o) / (score_p + score_o)
    return 0

def heuristic(max_player, env):
    m = mobility(max_player, env)
    p = coin_parity(max_player, env)
    c, max_c, min_c = corners_captured(max_player, env)
    s = stability_heuristic(max_player, env, max_c, min_c)
    l = corner_closeness(max_player, env)
    # print(10*m + 70*p + 800*c + 50*s - 300*l)
    return 10*m + 70*p + 800*c + 50*s - 300*l
