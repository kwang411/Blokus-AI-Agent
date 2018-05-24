'''
test.py:
    simple test harness to simulate some games
'''
from game import Game

p = Game(1,0)
numGames = 10
netScore1 = 0
for i in range (numGames):
    netScore1 += p.simulateGame()

p = Game(0,1)
netScore2 = 0
for i in range (numGames):
    #subtract because we want player 2's score
    netScore2 -= p.simulateGame()
print('average score of simpleeval, going first vs baseline over '+str(numGames)+' games: ' + str(netScore1*1.0/numGames))
print('average score of simpleeval, going second vs baseline over '+str(numGames)+' games: ' + str(netScore2*1.0/numGames))
