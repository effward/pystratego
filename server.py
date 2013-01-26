import pygame, sys, os, threading
import board, player
from pygame.locals import *
from constants import *
from helper import *
from network_server import *
from player import Player
from game import Game

games = {}
placements = {}

def check_move(game_name, move):
    game = games[game_name]
    turn = int(move[0])
    #print 'turn: ' + move[0]
    if turn is -1:
        #print 'player: ' + move[1]
        for piece in game.players[get_color_id(move[1])].pieces:
            #print 'type: ' + move[2]
            if piece.off_board() and piece.type == move[2]:
                #print 'pos: ' + move[5] + ', ' + move[6]
                #print str(piece.x) + ',' + str(piece.y)
                piece.move(int(move[5]), int(move[6]))
                #print str(piece.x) + ',' + str(piece.y)
                body = 'MOVE:' + move[0] + ':' + move[1] + ':' + move[5] + ':' + move[6]
                readyToStart = True
                for p in game.players:
                    readyToStart = readyToStart and p.ready()
                if readyToStart:
                    game.turn = 0
                return True, body, None
    else:
        turnPlayer = game.turn % NUM_PLAYERS
        combat = None
        #print 'turn: ' + str(turn) + '; game.turn: ' + str(game.turn) + '; color_id: ' + str(get_color_id(move[1])) + '; turnPlayer: ' + str(turnPlayer)
        if turn is game.turn and get_color_id(move[1]) is turnPlayer:
            for piece in game.players[get_color_id(move[1])].pieces:
                #print 'move_type: ' + move[2] + '; piece.type: ' + piece.type + '; x: ' + move[3] + '; piece.x: ' + str(piece.x) + '; y: ' + move[4] + '; piece.y: ' + str(piece.y)
                if piece.type == move[2] and piece.x is int(move[3]) and piece.y is int(move[4]):
                    selectedMoves = possible_moves(piece, game.board, game.players)
                    for x, y in selectedMoves:
                        #print 'move_x: ' + move[5] + '; x: ' + str(x) + '; move_y: ' + move[6] + '; y: ' + str(y)
                        if x is int(move[5]) and y is int(move[6]):
                            piece.move(x,y)
                            #print 'piece moved: move_x: ' + move[5] + '; x: ' + str(x) + '; move_y: ' + move[6] + '; y: ' + str(y)
                            body = 'MOVE:' + move[0] + ':' + move[1] + ':' + move[3] + ':' + move[4] + ':' + move[5] + ':' + move[6]
                            game.turn += 1
                            for player in game.players:
                                if not(piece.color == player.color):
                                    for p in player.pieces:
                                        defender = p.click_check(piece.rect)
                                        if defender is not None:
                                            result = fight(piece, defender)
                                            player_def = game.players[get_color_id(defender.color)]
                                            player_atk = game.players[get_color_id(piece.color)]
                                            if result is 1:
                                                combat = 'COMBAT:' + move[0] + ':ATTACKER:' + piece.type + ':' + defender.type
                                                player_def.kill(defender, player_atk)
                                            else:
                                                combat = 'COMBAT:' + move[0] + ':DEFENDER:' + piece.type + ':' + defender.type
                                                player_atk.kill(piece, player_def)
                                            break
                                    if combat:
                                        break
                            return True, body, combat
    return False, None, None
                        
        

def main():
    pygame.init()
    
    #screen = pygame.display.set_mode(SCREEN_SIZE)
    #pygame.display.set_caption('pyStratego Server')
    
    network = EchoComponent('pystratego.andrew-win7', 'hello123', 'andrew-win7', '5275', 'lobby@stratego.andrew-win7', 'Admin', 'stratego.andrew-win7', get='all')
    print("Done")
    while 1:
        # TODO: Add threads that service the event queue to deal with multiple connections at once
        for event in pygame.event.get():
            if event.type == QUIT: 
                sys.exit()
            elif event.type == NETWORK:
                if event.msg == 'check_move':
                    result, body, combat = check_move(event.game_name, event.move)
                    if result:
                        if int(event.move[0]) is -1:
                            pls = placements.setdefault(event.game_name, [])
                            pls.append(body)
                            placements[event.game_name] = pls
                            """
                            gameReady = True
                            for player in games[event.game_name].players:
                                for piece in player.pieces:
                                    if piece.off_board():
                                        gameReady = False
                            if gameReady:
                            """
                            if len(pls) is 52:
                                for placement in placements[event.game_name]:
                                    network.event('broadcast', (event.game_name, placement))
                        else:
                            network.event('broadcast', (event.game_name, body))
                    else:
                        print '**************************'
                        print '**************************'
                        print 'Cheating detected!'
                        print '**************************'
                        print '**************************'
                    if combat:
                        network.event('broadcast', (event.game_name, combat))
                elif event.msg == 'create_game':
                    games[event.game_name] = Game(event.game_name)
                elif event.msg == 'player_joined':
                    print 'New player joined ' + event.game_name
                    #if event.game_name in games:
                        #print 'Game found, updating player ' + str(event.color_id)
                        #game = games[event.game_name]
                        #for player in game.players:
                            #for piece in player.pieces:
                                #print 'Checking (' + str(piece.x) + ', ' + str(piece.y) + ')'
                                #if not(piece.off_board()):
                                    #print 'Sending piece'
                                    #body = 'PLACEMENT:-1:' + piece.color + ':' + str(piece.x) + ':' + str(piece.y)
                                    #network.event('send_move', (event.game_name, event.jid, body))
                else:
                    print '**************************'
                    print event.msg
                    print '**************************'

if __name__ == '__main__': main()