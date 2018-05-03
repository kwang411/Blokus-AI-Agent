from copy import copy
from random import choice
import gameUtil

class Game:
    def __init__(self):
        self.board = gameUtil.Board()
        self.tiles1 = gameUtil.tiles1
        self.tiles2 = gameUtil.tiles2

    #state consists of (board, player 1's hand, player 2's hand, player's turn, isFirstTurn)
    def getStartState(self):
        hand1 = [True for i in range(21)]
        hand2 = [True for i in range(21)]
        return (self.board.data, hand1, hand2, 1, True)

    #actions consist of (tileID, x_pos, y_pos, rotation_index, reflection_index)
    def getActions(self, state):
        data, hand1, hand2, turn, isFirstTurn = state
        actions = []
        tiles = self.tiles1
        hand = hand1
        if(turn == -1):
            tiles = self.tiles2
            hand = hand2
        for (tileId, inHand) in enumerate(hand):
            if (inHand):
                for x in range(self.board.width):
                    for y in range(self.board.height):
                        for rotationIndex in range(4):
                            for reflectionIndex in range(2):
                                if (self.board.canPlaceTile(tiles[tileId], x, y, rotationIndex, reflectionIndex, data, isFirstTurn)):
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
            newData = self.board.getNextBoard(data, self.tiles1[tileId], x, y, rotationIndex, reflectionIndex)
            return (newData, newHand, hand2, -turn, isFirstTurn)
        else:
            newHand = copy(hand2)
            newHand[tileId] = False
            newData = self.board.getNextBoard(data, self.tiles2[tileId], x, y, rotationIndex, reflectionIndex)
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
                score1 -= self.tiles1[tileId].squares
        for (tileId, inHand) in enumerate(hand2):
            if(inHand):
                score2 -= self.tiles2[tileId].squares
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
            parityMoves = [action for action in actions if self.game.tiles1[action[0]].squares == i]
            if(len(parityMoves) > 0):
                return choice(parityMoves)

class PlayGame:
    def __init__(self):
        self.game = Game()
        self.agent = BaselineAgent(self.game)
        self.state = self.game.getStartState()

    def p(self):
        print(self.game.board)

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

    def simulateGame(self):
        while(self.next(False)):
            pass

    def clearGame(self):
        self.game = Game()
        self.state = self.game.getStartState()

#simulates 2 games
#currently aggressively unoptimized, so takes a few seconds to play out a whole game
p = PlayGame()
p.simulateGame()
p.clearGame()
p.simulateGame()
