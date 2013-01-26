import pygame
import helper
from constants import *

class Marker(pygame.sprite.Sprite):
    def __init__(self, player):
        # Call Sprite initializer
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = helper.load_image('marker.bmp', -1)
        self.rect.center = self.getPlayerPos(player)
        self.player = player
        
    def move(self, player):
        self.player = player
        self.rect.center = self.getPlayerPos(player)

    def getPlayerPos(self, player):
        if player is 0:
            return helper.getPos(12,14)
            #i = SCREEN_WIDTH / 2
            #j = SCREEN_HEIGHT - self.rect.height
        elif player is 1:
            return helper.getPos(0,12)
            #i = BOARD_OFFSET_X - self.rect.width
            #j = SCREEN_HEIGHT / 2
        elif player is 2:
            return helper.getPos(2,0)
            #i = SCREEN_WIDTH / 2
            #j = 0
        elif player is 3:
            return helper.getPos(14,2)
            #i = BOARD_OFFSET_X + TILE_SIZE * BOARD_SIZE
            #j = SCREEN_HEIGHT / 2
        else:
            return (0,0)
            #i = 0
            #j = 0
        #return (i,j)
        
class TurnMarker(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.marker = Marker(0)
        self.add(self.marker)
    
    def move(self, player):
        self.marker.move(player)