import pygame, sys, os, threading
import board, player
from pygame.locals import *
from constants import *
from helper import *
from network_server import *
from player import Player
from game import Game

games = {}

def check_move(game_name, move):
	game = games[game_name]
	turn = int(move[0])
	if turn is -1:
		for piece in game.players[get_color_id(move[1])].pieces:
			if piece.type == move[2]:
				print str(piece.x) + ',' + str(piece.y)
				piece.move(int(move[5]), int(move[6]))
				print str(piece.x) + ',' + str(piece.y)
				body = 'MOVE:' + str(turn) + ':' + move[1] + ':' + move[5] + ':' + move[6]
				return True, body
		

def main():
	pygame.init()
	
	#screen = pygame.display.set_mode(SCREEN_SIZE)
	#pygame.display.set_caption('pyStratego Server')
	
	network = EchoComponent('pystratego.andrew-win7', 'hello123', 'andrew-win7', '5275', 'lobby@stratego.andrew-win7', 'Admin', 'stratego.andrew-win7', get='all')
	print("Done")
	while 1:
		for event in pygame.event.get():
			if event.type == QUIT: 
				sys.exit()
			elif event.type == NETWORK:
				if event.msg == 'check_move':
					result, body = check_move(event.game_name, event.move)
					if result:
						network.event('broadcast_move', (event.game_name, body))
					else:
						print '**************************'
						print '**************************'
						print 'Cheating detected!'
						print '**************************'
						print '**************************'
				elif event.msg == 'create_game':
					games[event.game_name] = Game(event.game_name)
				else:
					print '**************************'
					print event.msg
					print '**************************'

if __name__ == '__main__': main()