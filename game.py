from board import Board
from player import Player
from constants import *

class Game:
    def __init__(self, name, gui):
        self.name = name
        if gui:
            self.board = Board()
        else:
            self.board = Board(server=True)
        self.players = []
        for color in PLAYER_COLORS:
            if gui:
                self.players.append(Player(self.board, color))
            else:
                self.players.append(Player(self.board, color, server=True))
        self.turn = -1