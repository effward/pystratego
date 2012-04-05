import pygame, helper
import constants as const
from constants import *

class BoardTile(pygame.sprite.Sprite):
	def __init__(self, type, pos, server):
		# Call Sprite initializer
		pygame.sprite.Sprite.__init__(self)
		if server:
			self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
		else:
			self.image, self.rect = helper.load_image('tile' + type + '.bmp')
			self.altImage, self.altRect = None, None
			if type is '1':
				self.altImage, self.altRect = helper.load_image('tile' + type + '_hl.bmp')
		self.rect.center = pos
		self.type = type
		
	def click_check(self, mouseRect):
		if mouseRect.colliderect(self.rect):
			return self	
		return None

	def swap_highlight(self):
		if self.altImage is not None:
			tempImage = None
			tempImage = self.image
			self.image = self.altImage
			self.altImage = tempImage


	def update(self):
		pass
		
class Board(pygame.sprite.Group):
	def __init__(self, server=False):
		# Call Group initializer
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
		if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
			return False
		return self.tiles[x][y].type == '1'	
		
	def is_legal_lake(self, x, y):
		if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
			return False
		return self.tiles[x][y].type == '2'
