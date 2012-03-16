import pygame
import constants as const

class BoardTile(pygame.sprite.Sprite):
	def __init__(self, type, pos):
		# Call Sprite initializer
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = load_image('tile' + type + '.bmp', -1)
		self.rect.center = pos
		
	def update(self):
		pass
		
class Board(pygame.sprite.Group):
	def __init__(self):
		# Call Group initializer
		pygame.sprite.Sprite.__init__(self)
		self.tiles = []
		for i in range(15):
			tempList = []
			for j in range(15):
				if i < 3:
					if j < 4:
						tempList.add(BoardTile(0, (i*