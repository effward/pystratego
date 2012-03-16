import pygame

class Piece(pygame.sprite.Sprite):
	def __init__(self, color, type, pos):
		# Call Sprite initializer
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = helper.load_image('piece_' + color + type + '.bmp')
		self.rect.center = pos