from board import Board
from player import Player
from constants import *

class Game:
	def __init__(self, name):
		self.name = name
		self.board = Board(server=True)
		self.players = []
		for color in PLAYER_COLORS:
			self.players.append(Player(self.board, color, server=True))
		self.turn = -1