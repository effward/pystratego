import pygame, sys, random, os
import helper, board
import constants as const
from pygame.locals import *

def main():
	pygame.init()
	random.seed()

	screen = pygame.display.set_mode(const.SCREEN_SIZE)
	pygame.display.set_caption('pyStratego')
	
	background, background_rect = helper.load_image("bg.bmp")
	screen.blit(background, (0,0))
	
	b = board.Board()
	
	running = 1
	
	while running:
		for event in pygame.event.get():
			if event.type == QUIT: sys.exit()
			# Process Keyboard input
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = 0
					
		b.clear(screen, background)
		b.update()
		b.draw(screen)
					
		pygame.display.flip()
		
if __name__ == '__main__': main()