from copy import copy
from random import choice
from gameUtil import Board
from gameUtil import tiles
import gameUtil


#GameState class stores the current state of a game.
#includes getActions, generateSuccessor, and accessors for all stored data
#any agent accessing state data should only need to use these helper functions, 
#   not directly access the data or use board sub-functions
class GameState:
    def __init__(self, prevState = None):
        #if no previous, initialize to start state, otherwise full copy
        if (prevState == None): 
            self.hand1 = [True for i in range(21)]
            self.hand2 = [True for i in range(21)]
            self.playerTurn = 1
            self.isFirstTurn = True
            self.board = Board()
        else: 
            self.hand1 = copy(prevState.hand1)
            self.hand2 = copy(prevState.hand2)
            self.playerTurn = prevState.playerTurn
            self.isFirstTurn = prevState.isFirstTurn
            self.board = Board(prevState.board)

    def getHand1(self) :
        return self.hand1
    
    def getHand2(self):
        return self.hand2

    def getPlayerTurn(self):
        return self.getPlayerTurn

    def isFirstTurn(self):
        return self.isFirstTurn
 
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
                        for rotationIndex in range(4):
                            for reflectionIndex in range(2):
                                if (self.board.canPlaceTile(tileId, x, y, rotationIndex, reflectionIndex, self.playerTurn, self.isFirstTurn)):
                                    actions.append( (tileId, x, y, rotationIndex, reflectionIndex) )
        return actions

    #returns the state that follows the given action
    def generateSuccessor(self, action):
        #copy current state
        state = GameState(self)

        if (state.isFirstTurn and (state.playerTurn==-1)):
            state.isFirstTurn = False
        #pass: update turn only
        if (action == 'pass' or action == None):
            state.playerTurn = -state.playerTurn
            return state

        tileId, x, y, rotationIndex, reflectionIndex = action
        
        #player plays tile: update turn, player's hand, board
        if (state.playerTurn == 1):
            state.hand1[tileId] = False
        else:
            state.hand2[tileId] = False
        state.board.placeTile(tileId, x, y, rotationIndex, reflectionIndex, state.playerTurn)
        state.playerTurn = -state.playerTurn
        return state

    #return whether we have an end state (neither player has any actions)
    def isEnd(self):
        return ( (self.getActions() == []) and (self.getActions(True)  == []) )

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
        return score2-score1

    def p(self):
        print(self.board)


class Game:
    def __init__(self):
        self.board = gameUtil.Board()
        self.tiles = gameUtil.tiles






class BaselineAgent:
    def __init__(self):
        pass

    def getAction(self, gameState):
        actions = gameState.getActions()
        if (actions == []):
            return 'pass'
        
        #choose random move of moves worth the most squares
        for i in range(5,0,-1):
            parityMoves = [action for action in actions if tiles[action[0]].squares == i]
            if(len(parityMoves) > 0):
                return choice(parityMoves)
        
        #this shouldn't ever get here, but just in case pass
        return 'pass'



#class to run simulations of blockus games, either agent against self or player against agent
class Game:
    def __init__(self):
        self.gameState = GameState()
        self.agent = BaselineAgent()

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
    def checkPlace(self, tileId, x, y, rot = 0, ref = 0):
        return gameState.board.canPlaceTile(tileId, x, y, rot, ref, self.gameState.getPlayerTurn(), self.gameState.isFirstTurn())

    #plays out a turn of player and opponent
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
    def next(self, toPrint = False, action = False):
        if (action == False):
            action = self.agent.getAction(self.gameState)
        
        self.gameState = self.gameState.generateSuccessor(action)
        
        if(self.gameState.isEnd()):
            print("game over. Player 2's net score: " + str(self.gameState.getUtility()))
            print("player 1's tiles remaining: ", [tileId for (tileId, inHand) in enumerate(self.gameState.getHand1()) if inHand])
            print("player 2's tiles remaining: ", [tileId for (tileId, inHand) in enumerate(self.gameState.getHand2()) if inHand])
            self.p()
            return False
        elif(toPrint):
            self.p()
        return True

    #function to play agent against self
    def simulateGame(self):
        while(self.next(False)):
            pass
        self.newGame()

    #start a new game by resetting all data
    def newGame(self):
        self.gameState = GameState()
        print('')
        self.p()


#currently we're aggressively unoptimized, so takes a few seconds to play out a whole game
p = Game()
p.simulateGame()

print('The Game object is game.p. To simulate a game against the AI, call p.simulateGame()')
print('To see how to play a game against the AI, call p.help()')
