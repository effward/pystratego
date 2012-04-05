import pygame, os, sys
from pygame.locals import *
from constants import *

# Determines the outcome of combat between the pieces attacker and defender
def fight(attacker, defender):
	try:
		aType = int(attacker.type)
		dType = int(defender.type)
		if aType >= dType:
			return 1
		else:
			return 0
	except:
		if attacker.type is 'B':
			aType = -1
		elif attacker.type is 'S':
			aType = -2
		elif attacker.type is 'F':
			aType = -3
		else:
			aType = int(attacker.type)
		if defender.type is 'B':
			dType = -1
		elif defender.type is 'S':
			dType = -2
		elif defender.type is 'F':
			dType = -3
		else:
			dType = int(defender.type)
		return 1


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

# Finds all available starting tiles for the selected piece
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

# Checks if there is a piece from a player other than p in the space x,y
def is_occupied_excluding(p, players, b, x, y):
	tileRect = b.tiles[x][y].rect
	for pl in players:
		if pl.color is p.color:
			continue
		for piece in pl.pieces:
			collision = piece.click_check(tileRect)
			if collision is not None:
				return True
	return False

# Finds all possible moves for the selected piece
# TODO: bombs can jump over units, should need a straight shot
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
		if not(is_occupied_excluding(p, players, board, x+1, y)) and not(is_occupied(p, board, x+1,y)):
			for i in range(x+2, BOARD_SIZE):
				if board.is_legal(i, y) and not(is_occupied(p, board, i, y)):
					moves.append((i,y))
					if is_occupied_excluding(p, players, board, i, y):
						break
				else:
					break
		if not(is_occupied_excluding(p, players, board, x-1, y)) and not(is_occupied(p, board,x-1, y)):
			for i in range(x-2, -1, -1):
				if board.is_legal(i,y) and not(is_occupied(p, board, i, y)):
					moves.append((i,y))
					if is_occupied_excluding(p, players, board, i, y):
						break
				else:
					break
		if not(is_occupied_excluding(p, players, board, x, y+1)) and not(is_occupied(p, board, x, y+1)):
			for i in range(y+2, BOARD_SIZE):
				if board.is_legal(x,i) and not(is_occupied(p, board, x, i)):
					moves.append((x,i))
					if is_occupied_excluding(p, players, board, x, i):
						break
				else:
					break
		if not(is_occupied_excluding(p, players, board, x, y-1)) and not(is_occupied(p, board, x, y-1)):
			for i in range(y-2, -1, -1):
				if board.is_legal(x,i) and not(is_occupied(p, board, x, i)):
					moves.append((x,i))
					if is_occupied_excluding(p, players, board, x, i):
						break
				else:
					break
	elif selected.type is '6':
		extraMoves = []
		for i,j in moves:
			if is_occupied_excluding(p, players, board, i, j) or is_occupied(p, board, i, j):
				continue
			if (i-1 is not x or j is not y) and board.is_legal(i-1, j) and not(is_occupied(p, board, i-1, j)):
				extraMoves.append((i-1,j))
			if (i is not x or j-1 is not y) and board.is_legal(i, j-1) and not(is_occupied(p, board, i, j-1)):
				extraMoves.append((i,j-1))
			if (i+1 is not x or j is not y) and board.is_legal(i+1, j) and not(is_occupied(p, board, i+1, j)):
				extraMoves.append((i+1,j))
			if (i is not x or j+1 is not y) and board.is_legal(i, j+1) and not(is_occupied(p, board, i, j+1)):
				extraMoves.append((i, j+1))
		for move in extraMoves:
			moves.append(move)
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
	# Remove any moves that would move onto friendly pieces
	toRemove = []
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
	
def get_color_id(color):
	if color == 'red':
		return 0
	if color == 'blue':
		return 1
	if color == 'dred':
		return 2
	if color == 'dblue':
		return 3
	

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
