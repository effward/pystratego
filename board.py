##########################################################################
## board.py
##
## Stratego BoardTile and Board classes, used to represent the Ultimate Stratego game board.
##
## by Andrew Francis
##########################################################################

import pygame, helper
import constants as const
from constants import *
        
# A single board tile on the game board
class BoardTile(pygame.sprite.Sprite):
    def __init__(self, type, pos, server):
        pygame.sprite.Sprite.__init__(self)
        
        # if the board is on the server, don't need to load the tile image
        if server:
            self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        else:
            self.image, self.rect = helper.load_image('tile' + type + '.bmp')
            self.altImage, self.altRect = None, None
            # if this tile is a basic tile, load the highlight image
            if type is '1':
                self.altImage, self.altRect = helper.load_image('tile' + type + '_hl.bmp')
                
        self.rect.center = pos
        self.type = type
        
    def click_check(self, mouseRect):
        """Returns itself if mouseRect intersects with this tile, null otherwise"""
        if mouseRect.colliderect(self.rect):
            return self    
        return None

    def swap_highlight(self):
        """Swaps the image displayed to make it look like the tile is (de)highlighted"""
        if self.altImage is not None:
            tempImage = None
            tempImage = self.image
            self.image = self.altImage
            self.altImage = tempImage

        
# An Ultimate Stratego game board, essentially a 2D list of BoardTiles
class Board(pygame.sprite.Group):
    def __init__(self, server=False):
        pygame.sprite.Group.__init__(self)
        self.tiles = [] 
        for x in range(const.BOARD_SIZE):
            tempList = []
            for y in range(const.BOARD_SIZE):
                tempPos =   x*const.TILE_SIZE + const.BOARD_OFFSET_X, y*const.TILE_SIZE + const.BOARD_OFFSET_Y
                # Out of bounds tiles
                if ((x < 3 or x > 11) and y < 4) or \
                    ((x < 4 or x > 10) and y < 3) or \
                    ((x < 3 or x > 11) and y > 10) or \
                    ((x < 4 or x > 10) and y > 11):
                    tempTile = BoardTile('0', tempPos, server)
                # Stockade tiles
                elif (x is 7 and y is 1) or \
                        (x is 1 and y is 7) or \
                        (x is 7 and y is 13) or \
                        (x is 13 and y is 7):
                    tempTile = BoardTile('3', tempPos, server)
                # Lake tiles
                elif ((x > 5 and x < 9) and y is 4) or \
                        ((x > 5 and x < 9) and y is 10) or \
                        (x is 4 and (y > 5 and y < 9)) or \
                        (x is 10 and (y > 5 and y < 9)):
                    tempTile = BoardTile('2', tempPos, server)
                # Normal tiles
                else:
                    tempTile = BoardTile('1', tempPos, server)
                tempList.append(tempTile)
                self.add(tempTile)
            self.tiles.append(tempList)
    
    def is_legal(self, x, y):
        """Returns True if (x,y) is a legal square to move into, False otherwise"""
        if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
            return False
        return self.tiles[x][y].type == '1'    
        
    def is_legal_lake(self, x, y):
        """Returns True if (x,y) is a lake square, False otherwise"""
        if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
            return False
        return self.tiles[x][y].type == '2'
