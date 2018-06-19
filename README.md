# CS221 Final Project
Trey Connelly, Kevin Hu, Kenneth Wang
Trey - game infrastructure and environment, Kevin - tuning of evaluation function, Kenneth - agent implementation (minimax and Monte Carlo Tree Search)

gameUtil.py: code controlling gameboard ('Board') and tiles ('Tile'). Should not need to be directly accessed for agent functionality, but may need to be queried for evaluation function. If you need to access something directly, let me know and I'll update the infrastructure to add a helper accessor.

game.py: code controlling state and functions for querying/evaluating states ('GameState'), and some stuff to run the game easily ('Game'). You can import this to directly play games

agents.py: code containing classes representing various agents. Currently we have a baseline agent for testing ('BaselineAgent'), and a depth-0 search agent which uses a state evaluation function

test.py: simple test harness for evaluating agents. Edit this to run tests
