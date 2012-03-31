import pygame, sys, random, os, threading
import board, player
from pygame.locals import *
from constants import *
from helper import *
from network_client import *
from pgu import gui
from hud import *

def main():
	pygame.init()
	random.seed()
	
	print '**********************1PYGAMEEEEE*************************************'

	client = None #Client('test@andrew-win7', 'hello123', 'test1@stratego.andrew-win7', 'testing123', 'stratego.andrew-win7', get='all')
	
	print '**********************2PYGAMEEEEE*************************************'
	
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
	players.append(player.Player(b, 'dred', True))
	players.append(player.Player(b, 'dblue', True))
	myPlayer = 0
	
	running = 1
	# 0 = pre-lobby, 1 = lobby, 2 = game-lobby, 3 = pre-game, 4 = game, 5 = post-game
	mode = 0
	turn = 0
	haveSelected = False
	selectedMoves = []
	selected = None
	turnPlayer = 0
	
	hud = load_hud(mode)
	
	while running:
		turnPlayer = turn % NUM_PLAYERS
		for event in pygame.event.get():
			if event.type == QUIT: sys.exit()
			# Process Keyboard input
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = 0
			# Check for mode changes
			if event.type == MODECHANGE:
				mode = event.mode
				if mode is 1:
					jid = event.nick + '@andrew-win7'
					print jid
					client = Client(jid, 'hello123', 'lobby@stratego.andrew-win7', event.nick, 'stratego.andrew-win7', get='all')
					#TEMPORARY FIX
					#mode = 2
					#END TEMP FIX
					hud.quit()
					hud = load_hud(mode)
					for i in range(10):
						n = 'test' + str(i)
						pygame.event.post(Event(CHATMESSAGE, nick=n, body='testing'))
					#chatBox.tr()
					#chatBox.td(gui.Label(str(("point at "))))
			# Process Mouse input
			elif event.type == MOUSEBUTTONUP:
				if event.button == 1:
					mouseRect = pygame.Rect(event.pos[0] - 5, event.pos[1] - 5, 10, 10)
					if mode is 3: #pre-game
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
					elif mode is 4: #playing
						if True: #turnPlayer is myPlayer:
							if haveSelected:
								for x,y  in selectedMoves:
									target = b.tiles[x][y].click_check(mouseRect)
									if target is not None and selected is not None:
										selected.move(x,y)
										haveSelected = False
										turn += 1
										for x,y in selectedMoves:
											b.tiles[x][y].swap_highlight()
										# Check if combat takes place
										for i in range(len(players)):
											if i is not turnPlayer:
												for piece in players[i].pieces:
													defender = piece.click_check(mouseRect)
													# Combat - see who wins
													if defender is not None:
														result = fight(selected, defender)
														if result is 0:
															selected.move(-1,-1)
														else:
															defender.move(-1,-1)
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
								for piece in players[turnPlayer].pieces.sprites():
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
			hud.event(event)
			
		# Clear the screen, update sprites, draw to screen
		screen.blit(background, (0,0))
		if mode in [3,4,5]:
			b.clear(screen, background)
			for p in players:
				p.pieces.clear(screen,background)
			b.update()
			for p in players:
				p.pieces.update()
			b.draw(screen)
			for p in players:
					p.pieces.draw(screen)
		hud.paint()
		screen.blit(titleImage, titleRect)
					
		pygame.display.flip()
		
		# Mode change logic
		if mode is 3:
			readyToStart = True
			for p in players:
				readyToStart = readyToStart and p.ready()
			if readyToStart:
				mode = 1
		
if __name__ == '__main__': main()
