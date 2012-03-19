import pygame, sys, random, os
import board, player
from pygame.locals import *
from constants import *
from helper import *

def main():
	pygame.init()
	random.seed()

	screen = pygame.display.set_mode(SCREEN_SIZE)
	pygame.display.set_caption('pyStratego')
	
	# Free to use texture from http://www.designbash.com/wp-content/uploads/2010/01/wood-table-texture-2.jpg
	background, background_rect = load_image("bg.bmp")
	screen.blit(background, (0,0))
	titleImage, titleRect = load_image("title.bmp")
	titleRect.center = (SCREEN_WIDTH/2, 20)
	screen.blit(titleImage, titleRect)
	
	b = board.Board()
	players = []
	#for i in ['red', 'red', 'red', 'red']:
	#	players.append(player.Player(i))
	players.append(player.Player(b, 'red', True))
	players.append(player.Player(b, 'blue', True))
	myPlayer = 0
	
	running = 1
	# 0 = pre-game, 1 = game, 2 = post-game
	mode = 0
	turn = 0
	haveSelected = False
	selectedMoves = []
	selected = None
	
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
					if mode is 0: #pre-game
						if haveSelected:
							for x,y in selectedMoves:
								target = b.tiles[x][y].click_check(mouseRect)
								if target is not None and selected is not None:
									selected.move(x,y)
									if starting_moves(selected, b, players) == []:
										mode = 1
										target = None
									for x,y in selectedMoves:
										b.tiles[x][y].swap_highlight()
									selectedMoves = []
									haveSelected = False
									selected = None
									break
							if target is None:
								for piece in players[myPlayer].pieces.sprites():
									selected = piece.click_check(mouseRect)
									if selected is not None:
										haveSelected = True
										for x,y in selectedMoves:
											b.tiles[x][y].swap_highlight()
										selectedMoves = starting_moves(selected, b, players)
										for x,y in selectedMoves:
											b.tiles[x][y].swap_highlight()
										break
						else:
							for piece in players[myPlayer].pieces.sprites():
								selected = piece.click_check(mouseRect)
								if selected is not None:
									haveSelected = True
									target = None
									for x,y in selectedMoves:
										b.tiles[x][y].swap_highlight()
									selectedMoves = starting_moves(selected, b, players)
									for x,y in selectedMoves:
										b.tiles[x][y].swap_highlight()
									break
					elif mode is 1: #playing
						if True: #turn % NUM_PLAYERS == myPlayer:
							if haveSelected:
								for x,y  in selectedMoves:
									target = b.tiles[x][y].click_check(mouseRect)
									if target is not None:
										selected.move(x,y)
										haveSelected = False
										turn += 1
										for x,y in selectedMoves:
											b.tiles[x][y].swap_highlight()
										selectedMoves = []
										selected = None
										break	
								if target is None:
									for piece in players[myPlayer].pieces.sprites():
										selected = piece.click_check(mouseRect)
										if selected is not None:
											haveSelected = True
											if not selected.trapped:
												for x,y in selectedMoves:
													b.tiles[x][y].swap_highlight()
												selectedMoves = possible_moves(selected, b, players)
												for x,y in selectedMoves:
													b.tiles[x][y].swap_highlight()
											break
							else:
								for piece in players[myPlayer].pieces.sprites():
									selected = piece.click_check(mouseRect)
									if selected is not None:
										haveSelected = True
										if not selected.trapped:
											for x,y in selectedMoves:
												b.tiles[x][y].swap_highlight()
											selectedMoves = possible_moves(selected, b, players)
											for x,y in selectedMoves:
												b.tiles[x][y].swap_highlight()
										break
					
		b.clear(screen, background)
		for p in players:
			p.pieces.clear(screen,background)
		b.update()
		for p in players:
			p.pieces.update()
		b.draw(screen)
		for p in players:
				p.pieces.draw(screen)
		screen.blit(titleImage, titleRect)
					
		pygame.display.flip()
		if mode is 0:
			readyToStart = True
			for p in players:
				readyToStart = readyToStart and p.ready()
			if readyToStart:
				mode = 1
		
if __name__ == '__main__': main()
