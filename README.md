# CS221 Final Project
Currently we have 2 files:
gameUtil.py: code controlling gameboard ('Board') and tiles ('Tile'). Should not need to be directly accessed for agent functionality, but may need to be queried for evaluation function. If you need to access something directly, let me know and I'll update the infrastructure to add a helper accessor.

game.py: code controlling state and functions for querying/evaluating states ('GameState'), and some stuff to run the game easily ('Game')

agents.py: code containing classes representing various agents. Currently we have a baseline agent for testing ('BaselineAgent'), and a depth-0 search agent which uses a state evaluation function

You should be able to see/play stuff just by importing game.py in the python terminal
