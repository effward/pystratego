import pygame, os
from pygame.locals import *

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