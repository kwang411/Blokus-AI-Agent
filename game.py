from copy import copy
from gameUtil import Board
from gameUtil import tiles
import gameUtil
from agents import BaselineAgent
from agents import EvaluationAgent
from agents import MCTSAgent

#GameState class stores the current state of a game.
#includes getActions, generateSuccessor, and accessors for all stored data
#any agent accessing state data should only need to use these helper functions, 
#not directly access the data or use board sub-functions
class GameState:
    def __init__(self, prevState = None):
        #if no previous, initialize to start state, otherwise full copy
        if (prevState == None): 
            self.hand1 = [True for i in range(21)]
            self.hand2 = [True for i in range(21)]
            self.playerTurn = 1
            self.board = Board()
            self.previousPlayerPassed = False
            self.endState = False
        else: 
            self.hand1 = copy(prevState.hand1)
            self.hand2 = copy(prevState.hand2)
            self.playerTurn = prevState.playerTurn
            self.board = Board(prevState.board)
            self.previousPlayerPassed = prevState.previousPlayerPassed
            self.endState = prevState.endState
    def getHand1(self) :
        return self.hand1
    
    def getHand2(self):
        return self.hand2

    #returns which player's turn it is
    def getPlayerTurn(self):
        return self.playerTurn

    #returns which turn in the game it is
    #not really accurate because doesn't account for passing but close enough for our purposes
    def getTurn(self):
        return 22-len([True for inHand in self.hand2 if inHand])

 
    #actions consist of (tileID, x_pos, y_pos, rotation_index, reflection_index)
    def getActions(self, opp = False):
        actions = []
        hand = self.hand1
        #check player 2's actions if it's player 2's turn xor we specified opponent's action
        if((opp) != (self.playerTurn == -1)):
            hand = self.hand2
        for (tileId, inHand) in enumerate(hand):
            if (inHand):
                for x in range(self.board.width):
                    for y in range(self.board.height):
                        #simple heuristic to test whether this tile is roughly close enough to a corner
                        if (self.board.nearCorner(x,y, tileId, self.playerTurn)):
                            for rotationIndex in range(4):
                                for reflectionIndex in range(2):
                                    if (self.board.canPlaceTile(tileId, x, y, rotationIndex, reflectionIndex, self.playerTurn)):
                                        actions.append( (tileId, x, y, rotationIndex, reflectionIndex) )
        return actions

    #returns the state that follows the given action
    def generateSuccessor(self, action):
        #copy current state
        state = GameState(self)

        #pass: update turn only
        if (action == 'pass' or action == None):
            state.playerTurn = -state.playerTurn
            if (self.previousPlayerPassed):
                state.endState = True
            else:
                state.previousPlayerPassed = True
            return state
        
        tileId, x, y, rotationIndex, reflectionIndex = action
        
        #player plays tile: update turn, player's hand, board
        if (state.playerTurn == 1):
            state.hand1[tileId] = False
        else:
            state.hand2[tileId] = False
        state.board.placeTile(tileId, x, y, rotationIndex, reflectionIndex, state.playerTurn)
        state.previousPlayerPassed = False
        state.playerTurn = -state.playerTurn
        return state

    #return whether we have an end state (both players just passed)
    def isEnd(self):
        return self.endState

    #returns score differential of end state based on blockus rules
    #5 extra points for ending on single square not yet implemented (will have to change state)
    def getUtility(self):
        score1 = 0
        score2 = 0
        for (tileId, inHand) in enumerate(self.hand1):
            if(inHand):
                score1 -= tiles[tileId].squares
        for (tileId, inHand) in enumerate(self.hand2):
            if(inHand):
                score2 -= tiles[tileId].squares
        if(score1 == 0):
            score1 += 15
        if(score2 == 0):
            score2 += 15
        return score1-score2

    def getWinner(self):
        if self.isEnd():
            if self.getUtility() > 0:
                return 1
            else:
                return -1

    def p(self):
        print(self.board)

    def string(self):
        return str(self.board) + str(self.getPlayerTurn()) # essentially a hash so we can use gameStates as keys, takes into account passing


    ## accessors for evaluation functions ##
    def getPlayerOneCorners(self):
        return self.board.numCorners1

    def getPlayerTwoCorners(self):
        return self.board.numCorners2

    def getPlayerCorners(self, player):
        if player == 1:
            return self.board.numCorners1
        else:
            return self.board.numCorners2

    def getStateSpan(self, opp = False):
        span = set([])
        hand = self.hand1
        #check player 2's actions if it's player 2's turn xor we specified opponent's action
        if((opp) != (self.playerTurn == -1)):
            hand = self.hand2
        for (tileId, inHand) in enumerate(hand):
            if (inHand):
                for x in range(self.board.width):
                    for y in range(self.board.height):
                        #simple heuristic to test whether this tile is roughly close enough to a corner
                        if (self.board.nearCorner(x,y, tileId, self.playerTurn)):
                            for rotationIndex in range(4):
                                for reflectionIndex in range(2):
                                    if (self.board.canPlaceTile(tileId, x, y, rotationIndex, reflectionIndex, self.playerTurn)):
                                        span |= self.board.getTileSpan(tileId, x, y, rotationIndex, reflectionIndex) 
        return span



#class to run simulations of blockus games, either agent against self or player against agent
class Game:
    def __init__(self, a1 = 0, a2 = 0):
        self.gameState = GameState()

        #choose agents based on initialization parameters (defaults to basicAgent)
        if (a1 == 0):
            self.agent1 = BaselineAgent()
        else:
            self.agent1 = MCTSAgent(1)
        
        if (a2 == 0):
            self.agent2 = BaselineAgent()
        else:
            self.agent2 = MCTSAgent(-1)

    #print out the current board state
    def p(self):
        self.gameState.p()

    ##functions for easy player access##

    #print the tile ids remaining in the player's hand
    def checkHand(self, player = 1):
        if (player == 1):
            print([tileId for (tileId, inHand) in enumerate(self.gameState.getHand1()) if inHand])
        else:
            print([tileId for (tileId, inHand) in enumerate(self.gameState.getHand2()) if inHand])

    #prints the tile diagram of given rotation/reflections
    def checkTile(self, tileId, rot = 0, ref = 0):
        tiles[tileId].transform(rot,ref,True)

    #checks if a given board placement is legal in current board state
    #we cheat a bit here by directly accessing board for player because it's faster than comparing to all actions
    def checkPlace(self, tileId, x, y, rot = 0, ref = 0, player = 1):
        return self.gameState.board.canPlaceTile(tileId, x, y, rot, ref, player)

    #plays out a turn of player and opponent
    #human player is always player 1
    def play(self, tileId, x, y, rot = 0, ref = 0):
        if(self.checkPlace(tileId,x,y,rot,ref) and self.gameState.getHand1()[tileId]):
            self.next(False, (tileId, x, y, rot, ref))
            self.next(True)
            return True
        else:
            return False

    def help(self):
        print("checkHand(player): check tiles in a player's hand")
        print("checkTile(tileId, rotationIndex, reflectionIndex): prints given tile orientation")
        print("checkPlace(tileid,x,y,rotationIndex,reflectionIndex): returns whether given orientation can be placed in given position")
        print("play(tileid,x,y,rotationIndex,reflectionIndex): places given tile and plays a turn of the game")
        print('note the the (x,y) coordinates refer to the bottom-left corner of the tile (even if there is no square there')
    ##end player access functions##

    #function to directly simulate a turn either of a player or an agent
    def next(self, toPrint = False, action = False, turn = -1):
        #if an action is supplied by player, use it. Otherwise, set action based on agent
        if (action == False):
            if (turn == 1):
                action = self.agent1.getAction(self.gameState)
            else:
                action = self.agent2.getAction(self.gameState)

        
        self.gameState = self.gameState.generateSuccessor(action)
        
        if(self.gameState.isEnd()):
            score = self.gameState.getUtility()
            print("game over. Score (for player 1): " + str(score))
            print("player 1's tiles remaining: ", [tileId for (tileId, inHand) in enumerate(self.gameState.getHand1()) if inHand])
            print("player 2's tiles remaining: ", [tileId for (tileId, inHand) in enumerate(self.gameState.getHand2()) if inHand])
            self.p()
            return False
        elif(toPrint):
            self.p()
        return True

    #function to play agent against self
    def simulateGame(self):
        while(self.next(False, False, 1) and self.next(False, False, -1)):
            pass
        utility = self.gameState.getUtility()
        self.newGame(False)
        return utility

    #start a new game by resetting all data
    def newGame(self, toPrint = True):
        self.gameState = GameState()
        print('')
        if toPrint:
            self.p()

