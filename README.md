# Othello-AI
Various AI methods to play the game of Othello

First method: minimax with alpha-beta pruning
  Othello is a game that can be played at a human level with low-depth minimax search, at least with a good heuristic.
  My heuristic uses corner placement, corner proximity, mobility, disc parity, and disc stability. These are combiend with
  various weights to get the full heuristic.
  
  GUI done in pygame. Computer or human players can be selected by changing the constants at the top of "game.py"
