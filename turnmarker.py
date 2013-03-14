##########################################################################
## turnmarker.py
##
## A sprite that marks who's turn it is.
##
## by Andrew Francis
##########################################################################
import pygame
import helper
from constants import *

# A marker, knows where to move for each player
class Marker(pygame.sprite.Sprite):
    def __init__(self, player):
        # Call Sprite initializer
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = helper.load_image('marker.bmp', -1)
        self.rect.center = self.getPlayerPos(player)
        self.player = player
        
    def move(self, player):
        """Moves to the correct position for player's turn"""
        self.player = player
        self.rect.center = self.getPlayerPos(player)

    def getPlayerPos(self, player):
        """Returns the pixel position of the marker for player"""
        if player is 0:
            return helper.getPos(12,14)
        elif player is 1:
            return helper.getPos(0,12)
        elif player is 2:
            return helper.getPos(2,0)
        elif player is 3:
            return helper.getPos(14,2)
        else:
            return (0,0)
        
# Sprite group to hold marker sprite
class TurnMarker(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.marker = Marker(0)
        self.add(self.marker)
    
    def move(self, player):
        self.marker.move(player)