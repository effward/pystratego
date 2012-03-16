import pygame, sys, random, os
import helper, board, player
import constants as const
from pygame.locals import *

def main():
	pygame.init()
	random.seed()

	screen = pygame.display.set_mode(const.SCREEN_SIZE)
	pygame.display.set_caption('pyStratego')
	
	# Free to use texture from http://www.designbash.com/wp-content/uploads/2010/01/wood-table-texture-2.jpg
	background, background_rect = helper.load_image("bg.bmp")
	screen.blit(background, (0,0))
	
	b = board.Board()
	player1 = player.Player('red')
	
	running = 1
	# 0 = pre-game, 1 = game, 2 = post-game
	mode = 0
	
	while running:
		for event in pygame.event.get():
			if event.type == QUIT: sys.exit()
			# Process Keyboard input
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = 0
			# Process Mouse input
			elif event.type == MOUSEBUTTONUP:
				if event.button == 1:
					mouseRect = pygame.Rect(event.pos[0] - 5, event.pos[1] - 5, 10, 10)
					for piece in player1.pieces.sprites():
						piece.click_check(mouseRect)
					
		b.clear(screen, background)
		b.update()
		b.draw(screen)
		
		player1.pieces.clear(screen, background)
		player1.pieces.update()
		player1.pieces.draw(screen)
					
		pygame.display.flip()
		
if __name__ == '__main__': main()