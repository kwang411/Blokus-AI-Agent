from gameUtil import tiles
from random import choice

import time

'''
Contains classes representing our various agent implementations.
'''

class Agent:
  """
  *Agent instance modified from pacman assignment*

  An agent must define a getAction method, but may also define the
  following methods which will be called if they exist:
 
  def registerInitialState(self, state): # inspects the starting state
  """
  def __init__(self):
    pass

  def getAction(self, gameState):
    """
    The Agent will receive a GameState and must return an action
    """
    raiseNotDefined()


class BaselineAgent (Agent):

    def getAction(self, gameState):
        actions = gameState.getActions()
        if (actions == []):
            return 'pass'
        
        #choose random move of moves worth the most squares
        for i in range(5,0,-1):
            parityMoves = [action for action in actions if tiles[action[0]].squares == i]
            if(len(parityMoves) > 0):
                return choice(parityMoves)
        



class EvaluationAgent (Agent):

    def __init__(self, player=-1, depth=1):
        self.player = player
        self.depth = depth


    #basic evaluation function scoring on number of 'playable' corners
    def evaluate(self, gameState):
        weights = [1,1,-1,1,-1]
        scoreScore = weights[0] * gameState.getUtility()* self.player
        cornerScore1 = weights[1] * gameState.getPlayerCorners(self.player) 
        cornerScore2 = weights[2] * gameState.getPlayerCorners(-self.player)
        spanScore1 = weights[3] * len(gameState.getStateSpan()) 
        spanScore2 = weights[4] * len(gameState.getStateSpan(True))
        return scoreScore + cornerScore1 + cornerScore2 + spanScore1 + spanScore2
    
    #depth limited search
    def getAction(self, gameState):
        def valueSearch(gameState, depth, turn, alpha, beta):
            if gameState.isEnd():
                return gameState.getUtility()
            if depth == 0:
                return self.evaluate(gameState)
            if turn == 0:
                current = float("-inf")
                for action in gameState.getActions():
                    current = max(current, valueSearch(gameState.generateSuccessor(action), depth, 1, alpha, beta))
                    alpha = max(alpha, current)
                    if beta <= alpha:
                        break
                return current
            else: 
                current = float("inf")
                for action in reversed(gameState.getActions()):
                    current = min(current, valueSearch(gameState.generateSuccessor(action), depth - 1, 0, alpha, beta))
                    beta = min(beta, current)
                    if beta <= alpha:
                        break
                return current

        actions = gameState.getActions()
        if (actions == []):
            return 'pass'
        
        
        depth = 0
        if (gameState.getTurn() > 9):
            depth = 2
        depth = 0
        print(len(actions))
        
        #time how long it takes to get an action
        start_time = time.time()
        
        scores = [valueSearch(gameState.generateSuccessor(action), depth, 1, float("-inf"), float("inf")) for action in reversed(actions)]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = choice(bestIndices)

        #output time
        print("turn: %s--- %s seconds ---" % (gameState.getTurn(),time.time() - start_time))
        return actions[chosenIndex]

