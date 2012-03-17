import pygame, os, sys
from pygame.locals import *
from constants import *

# Returns all starting tiles for given color
def starting_tiles(color, b):
	moves = []
	for i in range(4,11):
		if color is 'red':
			moves.append((i,13))
			moves.append((i,12))
		elif color is 'dred':
			moves.append((i,1))
			moves.append((i,2))
		elif color is 'blue':
			moves.append((1,i))
			moves.append((2,i))
		elif color is 'dblue':
			moves.append((13,i))
			moves.append((12,i))
	for x,y in moves:
		if not b.is_legal(x,y):
			moves.remove((x,y))
	return moves

# Finds all available starting tiles
def starting_moves(selected, b, players):
	moves = []
	for i in range(4,11):
		if selected.color is 'red':
			moves.append((i,13))
			moves.append((i,12))
		elif selected.color is 'dred':
			moves.append((i,1))
			moves.append((i,2))
		elif selected.color is 'blue':
			moves.append((1,i))
			moves.append((2,i))
		elif selected.color is 'dblue':
			moves.append((13,i))
			moves.append((12,i))
	toRemove = []
	for p in players:
		if p.color is selected.color:
			for i,j in moves:
				tileRect = b.tiles[i][j].rect
				if not b.is_legal(i,j):
					toRemove.append((i,j))
				else:
					for piece in p.pieces:
						if piece.click_check(tileRect) is not None:
							toRemove.append((i,j))
	for pos in toRemove:
		moves.remove(pos)
	return moves

# Checks if there is a piece from player p in the space x,y
def is_occupied(p, b, x, y):
	tileRect = b.tiles[x][y].rect
	for piece in p.pieces:
		collision = piece.click_check(tileRect)
		if collision is not None:
			return True
	return False

# Finds all possible moves for the selected piece
# TODO: Make so you can't move onto your own pieces
def possible_moves(selected, board, players):
	moves = []
	x = selected.x
	y = selected.y
	p = None
	for pl in players:
		if pl.color == selected.color:
			p = pl
	if p is None:
		print 'You are not a player in the game'
		sys.exit()
	if board.is_legal(x-1, y) and not(is_occupied(p, board, x-1, y)):
		moves.append((x-1,y))
	if board.is_legal(x, y-1) and not(is_occupied(p, board, x, y-1)):
		moves.append((x,y-1))
	if board.is_legal(x+1, y) and not(is_occupied(p, board, x+1, y)):
		moves.append((x+1,y))
	if board.is_legal(x, y+1):
		moves.append((x, y+1))
	if selected.type is '2':
		for i in range(x+1, BOARD_SIZE):
			if board.is_legal(i, y):
				moves.append((i,y))
			else:
				break
		for i in range(x-1, -1, -1):
			if board.is_legal(i,y):
				moves.append((i,y))
			else:
				break
		for i in range(y+1, BOARD_SIZE):
			if board.is_legal(x,i):
				moves.append((x,i))
			else:
				break
		for i in range(y-1, -1, -1):
			if board.is_legal(x,i):
				moves.append((x,i))
			else:
				break
	elif selected.type is '6':
		if board.is_legal(x-2, y):
			moves.append((x-2,y))
		if board.is_legal(x-1, y-1):
			moves.append((x-1,y-1))
		if board.is_legal(x, y-2):
			moves.append((x,y-2))
		if board.is_legal(x-1, y+1):
			moves.append((x-1,y+1))
		if board.is_legal(x+1, y-1):
			moves.append((x+1, y-1))
		if board.is_legal(x+1, y+1):
			moves.append((x+1,y+1))
		if board.is_legal(x+2, y):
			moves.append((x+2,y))
		if board.is_legal(x, y+2):
			moves.append((x,y+2))
	elif selected.type is 'B':
		pos = [(x-3,y),(x+3,y),(x,y-3),(x,y+3)]
		for i,j in pos:
			if not board.is_legal(i,j):
				continue
			tileRect = board.tiles[i][j].rect
			for p in players:
				if p.color is not selected.color:
					for piece in p.pieces:
						if piece.click_check(tileRect) is not None:
							moves.append((i,j))
							break
	toRemove = []
	for p in players:
		if p.color is selected.color:
			for i,j in moves:
				tileRect = board.tiles[i][j].rect
				for piece in p.pieces:
					if piece.click_check(tileRect) is not None:
						toRemove.append((i,j))
	for pos in toRemove:
		moves.remove(pos)
	return moves

# Converts indices to pixel coordinates on the board
def getPos(x,y):
	i = BOARD_OFFSET_X + TILE_SIZE * x 
	j = BOARD_OFFSET_Y + TILE_SIZE * y 
	return (i,j)

# Loads image with file name: file_name, if colorkey is specified
# all pixels that are the same color as the specified colorkey will be
# rendered as invisible
def load_image(file_name, colorkey=None):
	full_name = os.path.join('assets', file_name)
	
	try:
		image = pygame.image.load(full_name)
	except pygame.error, message:
		print 'Cannot load image:', full_name
		raise SystemExit, message
	
	# Converts image to SDL's internal format, increases blit speed
	image = image.convert()
	
	if colorkey is not None:
		# If specefied colorkey is -1, the color of the top left pixel is used
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	
	return image, image.get_rect()
	
# Loads sound with file name: file_name
def load_sound(file_name):
	# Dummy Class to return on error
	class No_Sound:
		def play(self): pass
		
	# If mixer was imported or initialized incorrectly, return dummy class
	if not pygame.mixer or not pygame.mixer.get_init():
		return No_Sound()
		
	full_name = os.path.join('assets', file_name)
	if os.path.exists(full_name) == False:
		sound = pygame.mixer.Sound(full_name)
	else:
		print 'File does not exist:', full_name
		return No_Sound
		
	return sound
