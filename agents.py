from gameUtil import tiles
from random import choice

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

    def __init__(self, player=-1, depth=5):
        self.player = player
        self.depth = depth


    #basic evaluation function scoring on number of 'playable' corners
    def evaluate(self, gameState):
        result = 0
        result += (gameState.getPlayerCorners(self.player) - gameState.getPlayerCorners(-self.player))
        return result
    
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
                for action in gameState.getActions():
                    current = min(current, valueSearch(gameState.generateSuccessor(action), depth - 1, 0, alpha, beta))
                    beta = min(beta, current)
                    if beta <= alpha:
                        break
                return current

        actions = gameState.getActions()
        if (actions == []):
            return 'pass'

        scores = [valueSearch(gameState.generateSuccessor(action), self.depth, 1, float("-inf"), float("inf")) for action in actions]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = choice(bestIndices)
        return actions[chosenIndex]

