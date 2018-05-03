from copy import deepcopy

class Board:
    #class to hold game board and pieces
    # a 0 represents an empty square
    # 1 represents a square belonging to player 1, and 2 a square belonging to player 2
    # 3 for special start position
    
    def __init__(self):
        self.width = 14
        self.height = 14
        #initialize 14x14 grid of points
        self.data =[[0 for y in range(self.height)] for x in range(self.width)]
        self.data[4][4] = 3
        self.data[9][9] = 3
        self.numPiecesPlayed = 0

    #str method basically copied from game.py in pacman assignment
    def __str__(self):

        #out = [[str(self.data[y][x])[0] for y in range(self.height)] for x in range(self.width)]
        #out.reverse()
        out = []
        out.append([str(i%10) for i in range(self.height)])
        for r in range(self.height):
            x = []
            for c in range(self.width):
                if(self.data[r][c] == 0):
                    x.append('.')
                elif(self.data[r][c] == 1):
                    x.append('O')
                elif(self.data[r][c] == 2):
                    x.append('X')
                else:
                    x.append(str(self.data[r][c]))
            x.append(' ' + str(r))
            out.append(x)
        out.reverse()
        return '\n'.join([''.join(z) for z in out])
        #return '\n'.join([' '.join(x) for x in out])

    #method for accessing data where key is (x,y) tuble
    def __getitem__(self,key):
        x,y = key
        if(x<0 or x>=self.width or y<0 or y>= self.height):
            return -1
        else:
            return self.data[x][y]

    def get(self,x,y,data):
        if(x<0 or x>=self.width or y<0 or y>= self.height):
            return -1
        else:
            return data[x][y]
    
    #set data using (x,y) tuple (for consistency with Tile)
    def __setitem__(self,key,item):
        x,y = key
        self.data[x][y] = item

    #like placeTile but returns a new board instead of updating the original board
    #assumes that tile placement is valid
    def getNextBoard(self, data, tile, x, y, rot = 0, ref = 0):
        nextBoard = deepcopy(data)
        tile.transform(rot,ref)
        for r in range(1,tile.tileHeight+1):
            for c in range(1,tile.tileWidth+1):
                if(tile[(r,c)] == 'P'):
                    nextBoard[y+r-1][x+c-1] = tile.player
        return nextBoard

    #add a tile to the Board (assumes that tile can be placed)
    #tile: a Tile object representing tile to be places
    #x,y: position on the board to place
    #rot: 90 degree multiple for rotation, ref: wheteher to reflect
    #safe: if true, make sure tile placement is legal first
    #p: if true, print grid after placement
    def placeTile(self, tile, x, y, rot = 0, ref = 0, safe = False, p = False):
        if(safe):
            if (not self.canPlaceTile(tile,x,y,rot,ref)):
                return False
        else:
            tile.transform(rot,ref)
        for r in range(1,tile.tileHeight+1):
            for c in range(1,tile.tileWidth+1):
                if(tile[(r,c)] == 'P'):
                    self[(y+r-1,x+c-1)] = tile.player
        self.numPiecesPlayed += 1
        if(p):
            print(self)
        return True


    #check whether a specific tile can be placed in the grid at this position
    #(x,y) are the coordinates of the bottom-left bounding box of the piece
    def canPlaceTile(self, tile, x, y, rot = 0, ref = 0, data = False, isFirstTurn = False):
        if (data == False):
            data = self.data
        if (not tile.transform(rot,ref)):
            return False
        tileWidth = tile.tileWidth
        tileHeight = tile.tileHeight
        if((tileWidth+x > self.width) or (tileHeight+y > self.height)):
            return False
        numCorners = 0
        if(not isFirstTurn):
            for r in range(tileHeight+2):
                for c in range(tileWidth+2):
                    if(tile[(r,c)] == 'P' and self.get(y+r-1,x+c-1,data) != 0):
                        return False
                    elif(tile[(r,c)] == 'N' and self.get(y+r-1,x+c-1,data) == tile.player):
                        return False
                    elif(tile[(r,c)] == 'C' and self.get(y+r-1,x+c-1,data) == tile.player):
                        numCorners+=1
        else:
            for r in range(1,tileHeight+1):
                for c in range(1,tileWidth+1):
                    if(tile[(r,c)] == 'P' and self.get(y+r-1,x+c-1,data) == 3):
                        numCorners+=1
        return (numCorners > 0)



class Tile:
    #class to represent a single tile under rotation
    #initialized from data grid files
    #note that data is a (tileWidth+2)x(tileHeight+2) array
    #symmetry level: 0 = no distinct transformations (1)
    #   1 = distinct under 90 degree rotation clockwise only (2)
    #   2 = distinct under 90 degree rotation clockwise and/or reflection (4)
    #   3 = distinct under 90, 180, 270 degree rotation clockwise, and reflection (8)
    def __init__(self, tileWidth, tileHeight, dataArray, symmetryLevel, player, squares):
        self.data = dataArray
        self.tileWidth = tileWidth
        self.tileHeight = tileHeight
        self.symmetryLevel = symmetryLevel
        self.rotation = 0
        self.reflection = 0
        self.player = player
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



#polyomino data (each data array is official piece name; o and b stand for orange and blue
board = Board()
#Tile(width,height,name,symmetry,player)
i1 = [['C','N','C'],['N','P','N'],['C','N','C']]
o1 = Tile(1,1,i1,0,1,1)
b1 = Tile(1,1,i1,0,2,1)

i2 = ['CNC','NPN','NPN','CNC']
o2 = Tile(1,2,i2,1,1,2)
b2 = Tile(1,2,i2,1,2,2)

i3 = ['CNC','NPN','NPN','NPN','CNC']
o3 = Tile(1,3,i3,1,1,3)
b3 = Tile(1,3,i3,1,2,3)

crooked3 = ['CNNC','NPPN','NPNC','CNC.']
o4 = Tile(2,2,crooked3,2,1,3)
b4 = Tile(2,2,crooked3,2,2,3)

i4 = ['CNC','NPN','NPN','NPN','NPN','CNC']
o5 = Tile(1,4,i4,1,1,4)
b5 = Tile(1,4,i4,1,2,4)

shortL = ['.CNC','.NPN','CNPN','NPPN','CNNC']
o6 = Tile(2,3,shortL,3,1,4)
b6 = Tile(2,3,shortL,3,2,4)

shortT = ['CNC.','NPNC','NPPN','NPNC','CNC.']
o7 = Tile(2,3,shortT,2,1,4)
b7 = Tile(2,3,shortT,2,2,4)

square = ['CNNC','NPPN','NPPN','CNNC']
o8 = Tile(2,2,square,0,1,4)
b8 = Tile(2,2,square,0,2,4)

shortZ = ['CNNC.','NPPNC','CNPPN','.CNNC']
o9 = Tile(3,2,shortZ,2,1,4)
b9 = Tile(3,2,shortZ,2,2,4)

i5 = ['CNC','NPN','NPN','NPN','NPN','NPN','CNC']
o10 = Tile(1,5,i5,1,1,5)
b10 = Tile(1,5,i5,1,2,5)

l = ['.CNC','.NPN','.NPN','CNPN','NPPN','CNNC']
o11 = Tile(2,4,l,3,1,5)
b11 = Tile(2,4,l,3,2,5)

n = ['.CNC','.NPN','CNPN','NPPN','NPNC','CNC.']
o12 = Tile(2,4,n,3,1,5)
b12 = Tile(2,4,n,3,2,5)

p = ['.CNC','CNPN','NPPN','NPPN','CNNC']
o13 = Tile(2,3,p,3,1,5)
b13 = Tile(2,3,p,3,2,5)

u = ['CNNC','NPPN','CNPN','NPPN','CNNC']
o14 = Tile(2,3,u,2,1,5)
b14 = Tile(2,3,u,2,2,5)

y = ['CNC.','NPNC','NPPN','NPNC','NPN.','CNC.']
o15 = Tile(2,4,y,3,1,5)
b15 = Tile(2,4,y,3,2,5)

t = ['CNC..','NPNNC','NPPPN','NPNNC','CNC..']
o16 = Tile(3,3,t,2,1,5)
b16 = Tile(3,3,t,2,2,5)

v = ['CNNNC','NPPPN','NPNNC','NPN..','CNC..']
o17 = Tile(3,3,v,2,1,5)
b17 = Tile(3,3,v,2,2,5)

w = ['..CNC','.CNPN','CNPPN','NPPNC','CNNC.']
o18 = Tile(3,3,w,2,1,5)
b18 = Tile(3,3,w,2,2,5)

z = ['CNC..','NPNNC','NPPPN','CNNPN','..CNC']
o19 = Tile(3,3,z,2,1,5)
b19 = Tile(3,3,z,2,2,5)

f = ['CNC..','NPNNC','NPPPN','CNPNC','.CNC.']
o20 = Tile(3,3,f,3,1,5)
b20 = Tile(3,3,f,3,2,5)

x = ['.CNC.','CNPNC','NPPPN','CNPNC','.CNC.']
o21 = Tile(3,3,x,0,1,5)
b21 = Tile(3,3,x,0,2,5)

#build the player's hands
tiles1 = [o1,o2,o3,o4,o5,o6,o7,o8,o9,o10,o11,o12,o13,o14,o15,o16,o17,o18,o19,o20,o21]
tiles2 = [b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12,b13,b14,b15,b16,b17,b18,b19,b20,b21]


#board.placeTile(b15,0,9,0,0)
print(board)
