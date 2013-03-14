##########################################################################
## server.py
##
## Main server loop
##
## by Andrew Francis
##########################################################################
import pygame, sys, os, threading
import board, player, turnmarker
from pygame.locals import *
from constants import *
from helper import *
from network_server import *
from player import Player, AIPlayer
from game import Game
from hud import *

games = {}
placements = {}

def check_move(game_name, move):
    game = games[game_name]
    turn = int(move[0])
    if turn is -1:
        for piece in game.players[get_color_id(move[1])].pieces:
            if piece.type == move[2] and piece.off_board():
                piece.move(int(move[5]), int(move[6]))
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
        if turn is game.turn and get_color_id(move[1]) is turnPlayer:
            for piece in game.players[get_color_id(move[1])].pieces:
                if piece.type == move[2] and piece.x is int(move[3]) and piece.y is int(move[4]):
                    selectedMoves = possible_moves(piece, game.board, game.players)
                    for x, y in selectedMoves:
                        if x is int(move[5]) and y is int(move[6]):
                            piece.move(x,y)
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
                            nextTurnPlayer = game.turn % NUM_PLAYERS
                            if game.players[nextTurnPlayer].is_ai:
                                pygame.event.post(Event(AI, msg='ai_move', game_name=game_name, id=nextTurnPlayer))
                            nextPlayerCanMove = False
                            for piece in game.players[nextTurnPlayer].pieces:
                                moves = possible_moves(piece, game.board, game.players)
                                if len(moves) > 0 and not(piece.killed or piece.trapped):
                                    nextPlayerCanMove = True
                            if not(nextPlayerCanMove):
                                pygame.event.post(Event(NETWORK, msg='skip_move', game_name=game_name, id=nextTurnPlayer))
                            return True, body, combat
    return False, None, None
                        
        

def main(gui=False):
    pygame.init()
    
    if gui:
        screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('pyStratego Server')
         # Free to use texture from http://www.designbash.com/wp-content/uploads/2010/01/wood-table-texture-2.jpg
        background, background_rect = load_image("bg.bmp")
        screen.blit(background, (0,0))
        titleImage, titleRect = load_image("title.bmp")
        titleRect.center = (SCREEN_WIDTH/2, 20)
        screen.blit(titleImage, titleRect)
        mode = 0
        currentGame = None
        marker = turnmarker.TurnMarker()
        hud = load_server_hud(mode)
    
    network = EchoComponent('pystratego.andrew-win7', 'hello123', 'andrew-win7', '5275', 'lobby@stratego.andrew-win7', 'Admin', 'stratego.andrew-win7', get='all')
    print("Done")
    while 1:
        # TODO: Add threads that service the event queue to deal with multiple connections at once
        for event in pygame.event.get():
            if event.type == QUIT: 
                sys.exit()
            elif event.type == MODECHANGE:
                mode = event.mode
                hud.quit()
                if mode is 0:
                    hud = load_server_hud(mode, games=games.keys())
                elif mode is 1:
                    currentGame = event.room
                    hud = load_server_hud(mode)
            elif event.type == AI:
                if event.msg == 'ai_move':
                    game = games[event.game_name]
                    game.players[event.id].move(game.board, game.players, game.turn)
            elif event.type == NETWORK:
                if event.msg == 'skip_move':
                    msg = 'MOVE:' + str(games[event.game_name].turn) + ':SKIP'
                    games[event.game_name].turn += 1
                    network.event('broadcast', (event.game_name, msg))
                    nextTurnPlayer = games[event.game_name].turn % NUM_PLAYERS
                    if games[event.game_name].players[nextTurnPlayer].is_ai:
                        pygame.event.post(Event(AI, msg='ai_move', game_name=event.game_name, id=nextTurnPlayer))
                if event.msg == 'check_move':
                    result, body, combat = check_move(event.game_name, event.move)
                    if result:
                        if int(event.move[0]) is -1:
                            pls = placements.setdefault(event.game_name, [])
                            pls.append(body)
                            placements[event.game_name] = pls
                            if len(pls) is 52:
                                for player in games[event.game_name].players:
                                    print '**************************'
                                    print 'SENDING NICK'
                                    print player.color
                                    print player.nick_plain
                                    print '**************************'
                                    msg = 'NICK:' + player.color + ':' + player.nick_plain
                                    network.event('broadcast', (event.game_name, msg))
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
                    games[event.game_name] = Game(event.game_name, gui)
                elif event.msg == 'add_ai':
                    if event.id < NUM_PLAYERS:
                        ai_player = AIPlayer(games[event.game_name].board, PLAYER_COLORS[int(event.id)], event.game_name, gui)
                        games[event.game_name].players[int(event.id)] = ai_player
                        msg = 'NICK:' + ai_player.color + ':' + ai_player.nick_plain
                        network.event('broadcast', (event.game_name, msg))
                elif event.msg == 'nick_received':
                    if event.game in games:
                        if int(event.id) < len(games[event.game].players):
                            games[event.game].players[int(event.id)].nick_plain = event.nick
                elif event.msg == 'player_joined':
                    print 'New player joined ' + event.game_name
                else:
                    print '**************************'
                    print event.msg
                    print '**************************'
            if gui and event:
                hud.event(event)
        if gui:
            screen.blit(background, (0,0))
            if mode is 1 and currentGame is not None:
                game = games[currentGame]
                marker.move(game.turn % NUM_PLAYERS)
                game.board.clear(screen, background)
                for p in game.players:
                    p.pieces.clear(screen,background)
                marker.clear(screen, background)
                game.board.update()
                for p in game.players:
                    p.pieces.update()
                    marker.update()
                game.board.draw(screen)
                for p in game.players:
                    p.pieces.draw(screen)
                    if p.nick:
                        screen.blit(p.nick, p.nickpos)
                marker.draw(screen)
            hud.paint()    
            pygame.display.flip()
            
if __name__ == '__main__': 
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-g', '-G', 'gui', 'GUI']:
            main(True)
    main()
