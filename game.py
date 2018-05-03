from copy import copy
from random import choice
import gameUtil

class Game:
    def __init__(self):
        self.board = gameUtil.Board()
        self.tiles = gameUtil.tiles

    #state consists of (board, player 1's hand, player 2's hand, player's turn, isFirstTurn)
    def getStartState(self):
        hand1 = [True for i in range(21)]
        hand2 = [True for i in range(21)]
        return (self.board.data, hand1, hand2, 1, True)

    #actions consist of (tileID, x_pos, y_pos, rotation_index, reflection_index)
    def getActions(self, state):
        data, hand1, hand2, turn, isFirstTurn = state
        actions = []
        hand = hand1
        if(turn == -1):
            hand = hand2
        for (tileId, inHand) in enumerate(hand):
            if (inHand):
                for x in range(self.board.width):
                    for y in range(self.board.height):
                        for rotationIndex in range(4):
                            for reflectionIndex in range(2):
                                if (self.board.canPlaceTile(self.tiles[tileId], x, y, rotationIndex, reflectionIndex, turn, data, isFirstTurn)):
                                    actions.append( (tileId, x, y, rotationIndex, reflectionIndex) )
        return actions

    #returns the state that follows the given action
    def getSuccessor(self, state, action):
        data, hand1, hand2, turn, isFirstTurn = state
        if (isFirstTurn and (turn==-1)):
            isFirstTurn = False
        if (action == 'pass'):
            return (data, hand1, hand2, -turn, isFirstTurn)
        tileId, x, y, rotationIndex, reflectionIndex = action
        if (turn == 1):
            newHand = copy(hand1)
            newHand[tileId] = False
            newData = self.board.getNextBoard(data, self.tiles[tileId], x, y, rotationIndex, reflectionIndex, turn)
            return (newData, newHand, hand2, -turn, isFirstTurn)
        else:
            newHand = copy(hand2)
            newHand[tileId] = False
            newData = self.board.getNextBoard(data, self.tiles[tileId], x, y, rotationIndex, reflectionIndex, turn)
            return (newData, hand1, newHand, -turn, isFirstTurn)

    #return whether we have an end state
    def isEnd(self, state):
        data, hand1, hand2, turn, isFirstTurn = state
        nextActions = self.getActions(state)
        return (self.getActions(state) == []) and (self.getActions( (data,hand1,hand2,-turn,False) ) == [])

    #returns score differential of end state based on blockus rules
    #5 extra points for ending on single square not yet implemented
    def getUtility(self, state):
        data, hand1, hand2, turn, isFirstTurn = state
        score1 = 0
        score2 = 0
        for (tileId, inHand) in enumerate(hand1):
            if(inHand):
                score1 -= self.tiles[tileId].squares
        for (tileId, inHand) in enumerate(hand2):
            if(inHand):
                score2 -= self.tiles[tileId].squares
        if(score1 == 0):
            score1 += 15
        if(score2 == 0):
            score2 += 15
        return score2-score1

class BaselineAgent:
    def __init__(self, game):
        self.game = game

    def getAction(self, state):
        actions = self.game.getActions(state)
        if (actions == []):
            return 'pass'
        for i in range(5,0,-1):
            parityMoves = [action for action in actions if self.game.tiles[action[0]].squares == i]
            if(len(parityMoves) > 0):
                return choice(parityMoves)



#class to run simulations of blockus games, either agent against self or player against agent
class PlayGame:
    def __init__(self):
        self.game = Game()
        self.agent = BaselineAgent(self.game)
        self.state = self.game.getStartState()

    #print out the current board state
    def p(self):
        print(self.game.board)

    ##functions for easy player access##

    #print the tile ids remaining in the player's hand
    def checkHand(self, player = 1):
        if (player == 1):
            print([tileId for (tileId, inHand) in enumerate(self.state[1]) if inHand])
        else:
            print([tileId for (tileId, inHand) in enumerate(self.state[2]) if inHand])

    #prints the tile diagram of given rotation/reflections
    def checkTile(self, tileId, rot = 0, ref = 0):
        self.game.tiles[tileId].transform(rot,ref,True)

    #checks if a given board placement is legal in current board state
    def checkPlace(self, tileId, x, y, rot = 0, ref = 0):
        return self.game.board.canPlaceTile(self.game.tiles[tileId],x,y,rot,ref,self.state[3],False,self.state[4])

    #plays out a turn of player and opponent
    def play(self, tileId, x, y, rot = 0, ref = 0):
        if(self.checkPlace(tileId,x,y,rot,ref) and self.state[1][tileId]):
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
            action = self.agent.getAction(self.state)
        #print(action)
        self.state = self.game.getSuccessor(self.state, action)
        self.game.board.data = self.state[0]
        if(toPrint):
            self.p()
        if(self.game.isEnd(self.state)):
            print("game over. Player 2's net score: " + str(self.game.getUtility(self.state)))
            print("player 1's tiles remaining: ", [tileId for (tileId, inHand) in enumerate(self.state[1]) if inHand])
            print("player 2's tiles remaining: ", [tileId for (tileId, inHand) in enumerate(self.state[2]) if inHand])
            self.p()
            return False
        return True

    #function to play agent against self
    def simulateGame(self):
        while(self.next(False)):
            pass
        self.newGame()

    #start a new game by resetting all data
    def newGame(self):
        self.game = Game()
        self.state = self.game.getStartState()
        print('')
        self.p()


#currently we're aggressively unoptimized, so takes a few seconds to play out a whole game
p = PlayGame()
p.simulateGame()

print('The PlayGame object is game.p. To simulate a game against the AI, call p.simulateGame()')
print('To see how to play a game against the AI, call p.help()')
