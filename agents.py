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

    def __init__(self, player=-1):
        self.player = player

    #basic evaluation function scoring on number of 'playable' corners and square score
    def evaluate(self, gameState, action):
        squareScore = tiles[action[0]].squares 
        successor = gameState.generateSuccessor(action)
        cornerScore =  successor.getPlayerOneCorners() - successor.getPlayerTwoCorners()
        if (self.player == 1):
            return squareScore+cornerScore
        return squareScore-cornerScore
        
    def getAction(self, gameState):
        actions = gameState.getActions()
        if (actions == []):
            return 'pass'
      
        #choose move from moves with the best evaluation score
        scores = [(self.evaluate(gameState,action),action) for action in actions]
        maxScore = max(scores)[0]
                
        return choice([action for (score,action) in scores if score == maxScore])
