import pygame, helper
import constants as const

class Piece(pygame.sprite.Sprite):
	def __init__(self, color, type, pos):
		# Call Sprite initializer
		pygame.sprite.Sprite.__init__(self)
		self.image, self.rect = helper.load_image('piece_' + color + type + '.bmp', -1)
		self.rect.center = pos
		self.type = type
		# Position on the board [0...14], -1 means pre-placement, -2 means captured
		self.x = -1
		self.y = -1
		self.x_velocity = 0
		self.y_velocity = 0
		
	def update(self):
		if self.x > 0 and self.y > 0:
			targetPos =  (self.x * const.TILE_SIZE + const.BOARD_OFFSET_X, self.y * const.TILE_SIZE + const.BOARD_OFFSET_Y)
			if self.rect.center is not targetPos:
				self.rect.move_ip((self.x_velocity, self.y_velocity))
			else:
				self.x_velocity = 0
				self.y_velocity = 0
			
		
class Player:
	def __init__(self, color):
		self.pieces = pygame.sprite.Group()
		self.pieces.add(Piece(color, '2', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 0)))
		self.pieces.add(Piece(color, '2', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 1)))
		self.pieces.add(Piece(color, '3', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 2)))
		self.pieces.add(Piece(color, '4', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 3)))
		self.pieces.add(Piece(color, '5', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 4)))
		self.pieces.add(Piece(color, '6', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 5)))
		self.pieces.add(Piece(color, '7', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 6)))
		self.pieces.add(Piece(color, '8', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 7)))
		self.pieces.add(Piece(color, '9', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 8)))
		self.pieces.add(Piece(color, '10', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 9)))
		self.pieces.add(Piece(color, 'S', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 10)))
		self.pieces.add(Piece(color, 'F', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 11)))
		self.pieces.add(Piece(color, 'B', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 12)))
			