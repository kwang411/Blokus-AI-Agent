from copy import deepcopy



class Board:
    #class to hold game board and pieces
    #helper functions should be used in gameState only; anything using game state shouldn't need to use these
    # each square in the grid is represented by a set of bit flags
    # a 0 represents an empty square
    # 1 represents a square belonging to player 1, and 2 a square belonging to player 2
    # 3 for special start position

    
    LAST_PLAYED, PLAYABLE_2, CORNER_2, PLAYED_2, PLAYABLE_1, CORNER_1, PLAYED_1 = (1 << 6, 1 << 5, 1 << 4, 1 << 3, 1 << 2, 1 << 1, 1)
    EMPTY = PLAYABLE_2 + PLAYABLE_1


    #initialize data or import from a previous board
    # data: 2D grid representing the board with tile encoding above
    #numPiecesPlayed: how many pieces have been played
    #corners1: playable corners for player 1
    #corners2: playable corners for player 2
    def __init__(self, prevBoard = None):
        self.width = 14
        self.height = 14
        
        #import data from previous state
        if (prevBoard != None):
            self.data = deepcopy(prevBoard.data)
            self.numPiecesPlayed = prevBoard.numPiecesPlayed
            self.corners1 = prevBoard.corners1[:]
            self.corners2 = prevBoard.corners2[:]
            self.numCorners1 = prevBoard.numCorners1
            self.numCorners2 = prevBoard.numCorners2
        #initialize 14x14 grid of points
        else:
            self.data =[[(self.EMPTY) for y in range(self.height)] for x in range(self.width)]
            #make the start state playable by adding a phantom corner piece
            self.data[4][4] += (self.CORNER_2 + self.CORNER_1)
            self.data[9][9] += (self.CORNER_2 + self.CORNER_1)
            self.numPiecesPlayed = 0
            self.corners1 = [(4,4),(9,9)]
            self.corners2 = [(4,4),(9,9)]
            self.numCorners1 = 2
            self.numCorners2 = 2

    #str method basically copied from game.py in pacman assignment
    def __str__(self):

        #out = [[str(self.data[y][x])[0] for y in range(self.height)] for x in range(self.width)]
        #out.reverse()
        out = []
        out.append([str(i%10) for i in range(self.height)])
        for r in range(self.height):
            x = []
            for c in range(self.width):
                '''
                if (self.data[r][c] & self.LAST_PLAYED)!=0:
                    self.data[r][c]-=self.LAST_PLAYED
                    if(self.data[r][c] & self.PLAYED_1)!=0:
                        x.append('\033[44m'+'#'+'\033[0m')
                    elif(self.data[r][c] & self.PLAYED_2) != 0:
                        x.append('\033[43m'+'@'+'\033[0m')
                else:
                '''
                if(self.data[r][c] & self.PLAYED_1)!=0:
                    x.append('\033[44m'+' '+'\033[0m')
                elif(self.data[r][c] & self.PLAYED_2) != 0:
                    x.append('\033[43m'+' '+'\033[0m')
                else:
                    x.append('.')
            x.append(' ' + str(r))
            out.append(x)
        out.reverse()
        return '\n'.join([''.join(z) for z in out])
        #return '\n'.join([' '.join(x) for x in out])

    #method for accessing data where key is (x,y) tuple
    def __getitem__(self,key):
        x,y = key
        if(x<0 or x>=self.width or y<0 or y>= self.height):
            #out of bounds: all flags set to false == 0
            return 0
        else:
            return self.data[x][y]
    
    #set data using (x,y) tuple (for consistency with Tile)
    def __setitem__(self,key,item):
        x,y = key
        self.data[x][y] = item

    #add a tile to the Board (assumes that tile can be placed), updating necessary data
    #tile: a Tile object representing tile to be places
    #x,y: position on the board to place
    #rot: 90 degree multiple for rotation, ref: wheteher to reflect
    #safe: if true, make sure tile placement is legal first (for human use)
    #toPrint: if true, print grid after placement
    def placeTile(self, tileId, x, y, rot = 0, ref = 0, player = 1, safe = False, toPrint = False):
        tile = tiles[tileId]
        if(safe):
            if (not self.canPlaceTile(tile,x,y,rot,ref, player)):
                return False
        else:
            tile.transform(rot,ref)

        #player 1 placement
        if player == 1:
            for r in range(0,tile.tileHeight+2):
                for c in range(0,tile.tileWidth+2):
                    data = self[(y+r-1,x+c-1)] 
                    if(tile[(r,c)] == 'P'):
                        #remove corners from count
                        if (data & self.CORNER_1) != 0:
                            self.corners1.remove((x+c-1,y+r-1))
                            self.numCorners1 -= 1
                        if (data & self.CORNER_2) != 0:
                            self.corners2.remove((x+c-1,y+r-1))
                            self.numCorners2 -= 1
                        #clear all flags except played for this player
                        self[(y+r-1,x+c-1)] = self.PLAYED_1 #+ self.LAST_PLAYED
                    elif(tile[(r,c)] == 'C'):
                        #add corner to the board if the square isn't already blocked or a corner
                        if ((data & self.PLAYABLE_1) != 0) and ((data & self.CORNER_1) == 0):
                            self.corners1.append((x+c-1,y+r-1))
                            self.numCorners1 += 1
                            #set corner flag
                            self[(y+r-1,x+c-1)] |= self.CORNER_1
                    elif(tile[(r,c)] == 'N'):
                        #make this tile unplayable for this player only, if it wasn't already
                        if ((data & self.PLAYABLE_1) != 0):
                            if ((data & self.CORNER_1) != 0):
                                self.corners1.remove((x+c-1,y+r-1))
                                self.numCorners1 -= 1
                                #clear corner flag
                                self[(y+r-1,x+c-1)] &= (~self.CORNER_1)
                            #clear playable flag
                            self[(y+r-1,x+c-1)] &=  (~self.PLAYABLE_1)
        #same thing but for player 2. I could probably collapse these but whatever
        else:
            for r in range(0,tile.tileHeight+2):
                for c in range(0,tile.tileWidth+2):
                    data = self[(y+r-1,x+c-1)] 
                    if(tile[(r,c)] == 'P'):
                        #remove corners from count
                        if (data & self.CORNER_1) != 0:
                            self.corners1.remove((x+c-1,y+r-1))
                            self.numCorners1 -= 1
                        if (data & self.CORNER_2) != 0:
                            self.corners2.remove((x+c-1,y+r-1))
                            self.numCorners2 -= 1
                        #clear all flags except played for this player
                        self[(y+r-1,x+c-1)] = self.PLAYED_2 #+ self.LAST_PLAYED
                    elif(tile[(r,c)] == 'C'):
                        #add corner to the board if the square isn't already blocked or a corner
                        if ((data & self.PLAYABLE_2) != 0) and ((data & self.CORNER_2) == 0):
                            self.corners2.append((x+c-1,y+r-1))
                            self.numCorners2 += 1
                            #set corner flag
                            self[(y+r-1,x+c-1)] |= self.CORNER_2
                    elif(tile[(r,c)] == 'N'):
                        #make this tile unplayable for this player only, if it wasn't already
                        if ((data & self.PLAYABLE_2) != 0):
                            if ((data & self.CORNER_2) != 0):
                                self.corners2.remove((x+c-1,y+r-1))
                                self.numCorners2 -= 1
                                #clear corner flag
                                self[(y+r-1,x+c-1)] &= (~self.CORNER_2)
                            #clear playable flag
                            self[(y+r-1,x+c-1)] &=  (~self.PLAYABLE_2)
        self.numPiecesPlayed += 1
        if(toPrint):
            print(self)
        return True


    #check whether a specific tile can be placed in the grid at this position
    #(x,y) are the coordinates of the bottom-left bounding box of the piece
    def canPlaceTile(self, tileId, x, y, rot = 0, ref = 0, player = 1):
        tile = tiles[tileId]
        if (not tile.transform(rot,ref)):
            return False
        tileWidth = tile.tileWidth
        tileHeight = tile.tileHeight
        #make sure we're not placing anything out of bounds
        if((tileWidth+x > self.width) or (tileHeight+y > self.height)):
            return False
        numCorners = 0
        #check that every square is going on a playable location, and on at least one corner
        if(player == 1):
            for r in range(1,tileHeight+1):
                for c in range(1,tileWidth+1):
                    if(tile[(r,c)] == 'P'):
                        data = self[(y+r-1,x+c-1)]
                        if (data & self.PLAYABLE_1) == 0:
                            return False
                        elif (data & self.CORNER_1) != 0:
                            numCorners+= 1
        #do the same but for player 2
        else:
            for r in range(1,tileHeight+1):
                for c in range(1,tileWidth+1):
                    if(tile[(r,c)] == 'P'):
                        data = self[(y+r-1,x+c-1)]
                        if (data & self.PLAYABLE_2) == 0:
                            return False
                        elif (data & self.CORNER_2) != 0:
                            numCorners+= 1
        return (numCorners > 0)


    def getTileSpan(self, tileId, x, y, rot = 0, ref = 0):
        span = set([])
        tile = tiles[tileId]
        tileWidth = tile.tileWidth
        tileHeight = tile.tileHeight
        #get set of tile indices
        for r in range(1,tileHeight+1):
            for c in range(1,tileWidth+1):
                if(tile[(r,c)] == 'P'):
                    span.add((y+r-1,x+c-1))
        return span

    #function to determine whether a particular tile at a particular location is roughly close enough to a courner
    #note that the tile coordinates are always lower-left, so we only need to check up and right
    def nearCorner(self,x,y,tileId,player):
        width = tiles[tileId].tileWidth
        height = tiles[tileId].tileHeight
        if (player == 1):
            corners = self.corners1
        else:
            corners = self.corners2
        for (cx,cy) in corners:
            if (cx >= x and cy >= y):
                if (cx-x < width and cy-y < height) or (cx-x < height and cy-y < width):
                    return True
        return False



class Tile:
    #class to represent a single tile under rotation
    #initialized from data grid files
    #note that data is a (tileWidth+2)x(tileHeight+2) array
    #symmetry level: 0 = no distinct transformations (1)
    #   1 = distinct under 90 degree rotation clockwise only (2)
    #   2 = distinct under 90 degree rotation clockwise and/or reflection (4)
    #   3 = distinct under 90, 180, 270 degree rotation clockwise, and reflection (8)
    def __init__(self, tileWidth, tileHeight, dataArray, symmetryLevel,squares):
        self.data = dataArray
        self.tileWidth = tileWidth
        self.tileHeight = tileHeight
        self.symmetryLevel = symmetryLevel
        self.rotation = 0
        self.reflection = 0
        self.squares = squares

    def __str__(self):
        out = []
        for r in range(self.tileHeight+2):
            x = []
            for c in range(self.tileWidth+2):
                if(self[(r,c)] == 'P'):
                    x.append('@')
                else:
                    x.append(' ')
            out.append(x)
        out.reverse()
        return '\n'.join([''.join(z) for z in out])

    def transform(self, rot, ref, p = False):
        rotated = self.rotate(rot)
        reflected = True
        if (self.reflection != ref):
            reflected = self.reflect()
        if(p):
            print(self)
        return (rotated and reflected)
    
    def reflect(self):
        if(self.symmetryLevel <2):
            return False
        self.reflection = (self.reflection+1)%2
        return True

    def rotate(self, i):
        if(self.symmetryLevel == 0):
            return (i == 0)
        elif((i > 1) and (self.symmetryLevel < 3)):
            return False
        elif((i%2)!=(self.rotation%2)):
            temp = self.tileWidth
            self.tileWidth = self.tileHeight
            self.tileHeight = temp
        self.rotation = i
        return True

    #takes a tuple of coordinates and returns the corresponding rotated/reflected value
    def __getitem__(self, key):
        #rotation not yet implemented
        y,x = key
        if(self.reflection==1):
            x = self.tileWidth+1-x
        if(self.rotation==1):
            temp = self.tileHeight+1-y
            y = x
            x = temp
        elif(self.rotation==2):
            x = self.tileWidth+1-x
            y = self.tileHeight+1-y
        elif(self.rotation==3):
            temp = self.tileWidth+1-x
            x = y
            y = temp
        return self.data[y][x]



#polyomino data (each data array is official piece name) 
#Tile(width,height,name,symmetryLevel)
i1 = [['C','N','C'],['N','P','N'],['C','N','C']]
o1 = Tile(1,1,i1,0,1)

i2 = ['CNC','NPN','NPN','CNC']
o2 = Tile(1,2,i2,1,2)

i3 = ['CNC','NPN','NPN','NPN','CNC']
o3 = Tile(1,3,i3,1,3)

crooked3 = ['CNNC','NPPN','NPNC','CNC.']
o4 = Tile(2,2,crooked3,2,3)

i4 = ['CNC','NPN','NPN','NPN','NPN','CNC']
o5 = Tile(1,4,i4,1,4)

shortL = ['.CNC','.NPN','CNPN','NPPN','CNNC']
o6 = Tile(2,3,shortL,3,4)

shortT = ['CNC.','NPNC','NPPN','NPNC','CNC.']
o7 = Tile(2,3,shortT,2,4)

square = ['CNNC','NPPN','NPPN','CNNC']
o8 = Tile(2,2,square,0,4)

shortZ = ['CNNC.','NPPNC','CNPPN','.CNNC']
o9 = Tile(3,2,shortZ,2,4)

i5 = ['CNC','NPN','NPN','NPN','NPN','NPN','CNC']
o10 = Tile(1,5,i5,1,5)

l = ['.CNC','.NPN','.NPN','CNPN','NPPN','CNNC']
o11 = Tile(2,4,l,3,5)

n = ['.CNC','.NPN','CNPN','NPPN','NPNC','CNC.']
o12 = Tile(2,4,n,3,5)

p = ['.CNC','CNPN','NPPN','NPPN','CNNC']
o13 = Tile(2,3,p,3,5)

u = ['CNNC','NPPN','CNPN','NPPN','CNNC']
o14 = Tile(2,3,u,2,5)

y = ['CNC.','NPNC','NPPN','NPNC','NPN.','CNC.']
o15 = Tile(2,4,y,3,5)

t = ['CNC..','NPNNC','NPPPN','NPNNC','CNC..']
o16 = Tile(3,3,t,2,5)

v = ['CNNNC','NPPPN','NPNNC','NPN..','CNC..']
o17 = Tile(3,3,v,2,5)

w = ['..CNC','.CNPN','CNPPN','NPPNC','CNNC.']
o18 = Tile(3,3,w,2,5)

z = ['CNC..','NPNNC','NPPPN','CNNPN','..CNC']
o19 = Tile(3,3,z,2,5)

f = ['CNC..','NPNNC','NPPPN','CNPNC','.CNC.']
o20 = Tile(3,3,f,3,5)

x = ['.CNC.','CNPNC','NPPPN','CNPNC','.CNC.']
o21 = Tile(3,3,x,0,5)

#build the player's hands
tiles = [o1,o2,o3,o4,o5,o6,o7,o8,o9,o10,o11,o12,o13,o14,o15,o16,o17,o18,o19,o20,o21]


