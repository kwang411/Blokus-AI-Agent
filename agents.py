from __future__ import division
from gameUtil import tiles
from random import choice,uniform

import time
from math import log, sqrt
import collections
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

    def __init__(self, player=-1, depth=0):
        self.player = player
        self.depth = depth


    #basic evaluation function scoring on number of 'playable' corners
    def evaluate(self, gameState):
        weights = [0.5,0,-1,0,0]
        scoreScore = weights[0] * gameState.getUtility()* self.player
        #cornerScore1 = weights[1] * gameState.getPlayerCorners(self.player) 
        cornerScore2 = weights[2] * gameState.getPlayerCorners(-self.player)
        #spanScore1 = weights[3] * len(gameState.getStateSpan()) 
        #spanScore2 = weights[4] * len(gameState.getStateSpan(True))
        return scoreScore + cornerScore2 #+ spanScore1 + spanScore2
    
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
        
        '''
        depth = 0
        if (gameState.getTurn() > 9):
            depth = 2
        print(len(actions))
        '''
        #time how long it takes to get an action
        start_time = time.time()
        
        scores = [valueSearch(gameState.generateSuccessor(action),self.depth, 1, float("-inf"), float("inf")) for action in actions]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = choice(bestIndices)

        #output time
        print("turn: %s--- %s seconds ---" % (gameState.getTurn(),time.time() - start_time))
        return actions[chosenIndex]


class MCTSAgent (Agent):

    def __init__(self, player):
        self.player = player
        self.C = 1.4
        self.turn_time = 30
        self.statistics = {} #collections.defaultdict(lambda: (0, 0)) 

    def simulation(self, gameState):
        expanded = False
        visited = set()
        currentState = gameState
        if currentState.string() not in self.statistics:
            self.statistics[currentState.string()] = [0.,0.]
        visited.add(currentState)
        turn = 1

        while(True) :
            actions = currentState.getActions()
            if (actions == []):
                currentState = currentState.generateSuccessor('pass')
            else:
                stateWeights = [(currentState.generateSuccessor(action),tiles[action[0]].squares) for action in actions]
                nextStates = [sw[0] for sw in stateWeights]
                if(all(state.string() in self.statistics for state in nextStates)):
                #UCB decision making based on exploration probability; max( ,1) to make sure no divide by 0's or ln(0); sorry for disgusting line
                    vals = [(turn*self.statistics[state.string()][0]/max(self.statistics[state.string()][1], 1) + 
                        self.C*sqrt(log(max(self.statistics.get(currentState.string(), (0,1))[1],1))/max(self.statistics[state.string()][1],1)), state) for state in nextStates]
                    ucb = max([val[0] for val in vals])
                    bestIndices = [index for (index,val) in enumerate(vals) if val[0] == ucb]
                    chosenIndex = choice(bestIndices)
                    currentState = vals[chosenIndex][1]
                else:#random playout
                    #currentState = choice(nextStates)
                    #random playout weighted by square score
                    currentState = weightedRandomChoice(stateWeights)

            turn *= -1
            visited.add(currentState)
            if not expanded and currentState.string() not in self.statistics:
                expanded = True
                self.statistics[currentState.string()] = [0.,0.]
            if currentState.isEnd():
                break

        #backpropagate result of playout
        reward = abs(currentState.getUtility())
        if currentState.getWinner() != self.player:
            reward *= -1
        for state in visited:
            if state.string() not in self.statistics: #only backpropagate to nodes in statistics
                continue
            self.statistics[state.string()][0] += reward # value
            self.statistics[state.string()][1] += 1 # number of visits

    def getAction(self, gameState):
        self.statistics.clear()
        actions = gameState.getActions()
        if (actions == []):
            return 'pass'

        # simulate a large number of playouts
        numberGames = 0
        start = time.time()
        while time.time() - start < self.turn_time:
            self.simulation(gameState)
            numberGames += 1

        print str(numberGames) + " simulations run for this action"
        # choose state that has been visited the most times
        visits = [(self.statistics[gameState.generateSuccessor(action).string()][1],actionIndex) for (actionIndex, action) in enumerate(actions) if gameState.generateSuccessor(action).string() in self.statistics]
        
        #print([(consideredAction,visits[i]) for (i,consideredAction) in enumerate(consideredActions)] )
        mostVisits = max([visit[0] for visit in visits])
        bestIndices = [actionIndex for (numVisits, actionIndex) in visits if numVisits == mostVisits]
        chosenIndex = choice(bestIndices)
        return actions[chosenIndex]

#modified from HW7-car
#weighted random choice from list of tuples
def weightedRandomChoice(weightDict):
    weights = []
    elems = []
    for elem in weightDict:
        weights.append(elem[1])
        elems.append(elem[0])
    total = sum(weights)
    key = uniform(0, total)
    runningTotal = 0.0
    chosenIndex = None
    for i in range(len(weights)):
        weight = weights[i]
        runningTotal += weight
        if runningTotal > key:
            chosenIndex = i
            return elems[chosenIndex]
    raise Exception('Should not reach here')
