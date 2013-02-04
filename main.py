import pygame, sys, random, os, threading, time
import board, player, turnmarker
from pygame.locals import *
from constants import *
from helper import *
from network_client import *
from player import Player, Piece
from pgu import gui
from hud import *

def main():
    pygame.init()
    random.seed()
    

    client = None #Client('test@andrew-win7', 'hello123', 'test1@stratego.andrew-win7', 'testing123', 'stratego.andrew-win7', get='all')
    
    
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('pyStratego')
    
    # Free to use texture from http://www.designbash.com/wp-content/uploads/2010/01/wood-table-texture-2.jpg
    background, background_rect = load_image("bg.bmp")
    screen.blit(background, (0,0))
    titleImage, titleRect = load_image("title.bmp")
    titleRect.center = (SCREEN_WIDTH/2, 20)
    screen.blit(titleImage, titleRect)
    
    b = board.Board()
    players = None
    #for i in ['red', 'red', 'red', 'red']:
    #    players.append(player.Player(i))
    myPlayer = 0
    
    running = 1
    # 0 = pre-lobby, 1 = loading/lobby, 2 = server-select, 3 = loading/game, 4 = pre-game, 5 = waiting for players, 6 = game, 7 = post-game
    mode = 0
    turn = -1
    haveSelected = False
    selectedMoves = []
    selected = None
    moved = None
    defender = None
    turnPlayer = 0
    moveLog = []
    ready = False
    marker = None
    move_sending = False
    
    hud = load_hud(mode)
    
    while running:
        turnPlayer = turn % NUM_PLAYERS
        # Mode change logic
        if mode is 4:
            if not ready:
                players[myPlayer].random_start(b)
            if players[myPlayer].ready():
                ready = True
                client.event('send_placement', players[myPlayer].pieces)
                pygame.event.post(Event(MODECHANGE, mode=5))
        if mode is 5:
            readyToStart = True
            for p in players:
                readyToStart = readyToStart and p.ready()
            if readyToStart:
                pygame.event.post(Event(MODECHANGE, mode=6))
        if mode is 6:
            result = is_game_over(players, b)
            if result is not None:
                pygame.event.post(Event(MODECHANGE, mode=7, winner=result))
        for event in pygame.event.get():
            if event.type == QUIT: 
                if client:
                    client.event('disconnect', None)
                sys.exit()
            # Process Keyboard input
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = 0
            # Check for network events:
            elif event.type == NETWORK:
                if event.msg == 'connected':
                    client.event("get_rooms", None)
                elif event.msg == 'got_rooms':
                    pygame.event.post(Event(MODECHANGE, mode=2))
                elif event.msg == 'joined_room':
                    pygame.event.post(Event(MODECHANGE, mode=4, room=event.room, me=event.count))
                elif event.msg == 'create_room':
                    client.event('create_room', event.room)
                elif event.msg == 'placement_received':
                    if int(event.turn) is -1 and not(get_color_id(event.color) is myPlayer):
                        pieceMoved = False
                        for piece in players[get_color_id(event.color)].pieces:
                            if piece.off_board():
                                piece.move(int(event.x), int(event.y))
                                pieceMoved = True
                                break
                        if not(pieceMoved):
                            client.event('move_error', (2, "Received a placement after all pieces have been placed."))
                elif event.msg == 'combat_received':
                    if int(event.turn) is turn:
                        player_def = players[get_color_id(defender.color)]
                        player_atk = players[get_color_id(moved.color)]
                        if defender.type == 'U':
                            temp_piece = Piece(defender.color, event.defender_type, defender.x, defender.y, False)
                            player_def.pieces.remove(defender)
                            player_def.pieces.add(temp_piece)
                            defender = temp_piece
                        if moved.type == 'U':
                            temp_piece = Piece(moved.color, event.attacker_type, moved.x, moved.y, False)
                            player_atk.pieces.remove(moved)
                            player_atk.pieces.add(temp_piece)
                            moved = temp_piece
                        if event.winner == 'ATTACKER':
                            player_def.kill(defender, player_atk)
                        elif event.winner == 'DEFENDER':
                            player_atk.kill(moved, player_def)
                        defender = None
                        moved = None
                        turn += 1
                        turnPlayer = turn % NUM_PLAYERS
                        marker.move(turnPlayer)
                elif event.msg == 'move_received':
                    color_id = get_color_id(event.color)
                    if int(event.turn) is turn and color_id is turnPlayer:
                        if not(color_id is myPlayer):
                            tileRect = b.tiles[int(event.x1)][int(event.y1)].rect
                        else:
                            tileRect = b.tiles[int(event.x2)][int(event.y2)].rect
                        for piece in players[color_id].pieces:
                            moved = piece.click_check(tileRect)
                            if moved is not None and not(color_id is myPlayer):
                                moved.move(int(event.x2), int(event.y2))
                                break
                            if moved is not None:
                                break
                        if moved is None:
                            client.event('move_error', (1, "Received a move for a piece that doesn't exist"))
                        else:
                            combatOccurs = False
                            for player in players:
                                if not(event.color == player.color):
                                    for piece in player.pieces:
                                        defender = piece.click_check(moved.rect)
                                        if defender is not None:
                                            combatOccurs = True
                                            break
                                    if combatOccurs:
                                        break
                            if not(combatOccurs):
                                turn += 1
                                turnPlayer = turn % NUM_PLAYERS
                                moved = None
                                marker.move(turnPlayer)
                                move_sending = False
                elif event.msg == 'failure':
                    print event.details
                else:
                    print '****************************************************************'
                    print '****************************************************************'
                    print 'Unexpected NETWORK message:'
                    print event.msg
                    print '****************************************************************'
                    print '****************************************************************'
                    #TODO: deal with network failures
            # Check for mode changes
            elif event.type == MODECHANGE:
                mode = event.mode
                if mode is 1: # loading screen
                    jid = event.nick + '@andrew-win7'
                    print jid
                    client = Client(jid, 'hello123', LOBBY_JID, event.nick, 'stratego.andrew-win7', get='all')
                elif mode is 2:
                    if players:
                        b = board.Board()
                        players = None
                        myPlayer = 0
                        turn = -1
                        haveSelected = False
                        selectedMoves = []
                        selected = None
                        moved = None
                        defender = None
                        turnPlayer = 0
                        moveLog = []
                        ready = False
                        marker = None
                        move_sending = False
                elif mode is 3:
                    room = event.room
                    client.event("join_room", room)
                elif mode is 4:
                    myPlayer = int(event.me)
                    players = []
                    for i in range(len(PLAYER_COLORS)):
                        if i == myPlayer:
                            players.append(Player(b, PLAYER_COLORS[i]))
                        else:
                            players.append(Player(b, PLAYER_COLORS[i], remote=True))
                    client.event('room_ready', event.room)
                    marker = turnmarker.TurnMarker()
                elif mode is 6:
                    turn = 0
                elif mode is 8:
                    client.event('leave_room')
                if mode is 7:
                    hud.quit()
                    hud = load_hud(mode, event.winner)
                else:
                    hud.quit()
                    hud = load_hud(mode)
                
            # Process Mouse input
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouseRect = pygame.Rect(event.pos[0] - 5, event.pos[1] - 5, 10, 10)
                    if mode is 4: #pre-game
                        if myPlayer < NUM_PLAYERS:
                            # If a piece is selected 
                            if haveSelected:
                                # check if the player clicked one of the possible moves
                                for x,y in selectedMoves:
                                    target = b.tiles[x][y].click_check(mouseRect)
                                    if target is not None and selected is not None:
                                        #client.event('send_move', (turn, selected.color, selected.type, selected.x, selected.y, x, y))
                                        #client.event('send_move', (turn, selected, selected.x, selected.y, x, y))
                                        selected.move(x,y)
                                        # Turn off highlights
                                        for x,y in selectedMoves:
                                            b.tiles[x][y].swap_highlight()
                                        selectedMoves = []
                                        haveSelected = False
                                        selected = None
                                        break
                                # If the player didn't click on a correct move
                                if target is None:
                                    # Check if they clicked on one of their other pieces
                                    for piece in players[myPlayer].pieces.sprites():
                                        temp = piece.click_check(mouseRect)
                                        # if so highlight moves for that piece
                                        if temp is not None:
                                            # If clicked selected piece, deselect it
                                            """
                                            if temp == selected:
                                                haveSelected = False
                                                selected = None
                                                for x,y in selectedMoves:
                                                    b.tiles[x][y].swap_highlight()
                                                break
                                            """
                                            haveSelected = True
                                            selected = temp
                                            for x,y in selectedMoves:
                                                b.tiles[x][y].swap_highlight()
                                            selectedMoves = starting_moves(selected, b, players[myPlayer])
                                            for x,y in selectedMoves:
                                                b.tiles[x][y].swap_highlight()
                                            break
                            # If no piece is selected
                            else:
                                # Check if player clicked on a piece
                                for piece in players[myPlayer].pieces.sprites():
                                    selected = piece.click_check(mouseRect)
                                    # If so, highlight it's possible moves
                                    if selected is not None:
                                        haveSelected = True
                                        target = None
                                        for x,y in selectedMoves:
                                            b.tiles[x][y].swap_highlight()
                                        selectedMoves = starting_moves(selected, b, players[myPlayer])
                                        for x,y in selectedMoves:
                                            b.tiles[x][y].swap_highlight()
                                        break
                    elif mode is 6: #playing
                        if turnPlayer is myPlayer and not(move_sending):
                            #print "haveSelected = " + str(haveSelected) + ", selected = " + str(selected)
                            if haveSelected:
                                for x,y  in selectedMoves:
                                    target = b.tiles[x][y].click_check(mouseRect)
                                    if target is not None and selected is not None:
                                        #client.event('send_move', (turn, selected.color, selected.type, selected.x, selected.y, x, y))
                                        client.event('send_move', (turn, selected, selected.x, selected.y, x, y))
                                        selected.move(x,y)
                                        haveSelected = False
                                        move_sending = True
                                        #turn += 1
                                        for x,y in selectedMoves:
                                            b.tiles[x][y].swap_highlight()
                                        """
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
                                                            """
                                        selectedMoves = []
                                        selected = None
                                        break    
                                if target is None:
                                    for piece in players[myPlayer].pieces.sprites():
                                        temp_selected = piece.click_check(mouseRect)
                                        if temp_selected is not None:
                                            haveSelected = True
                                            selected = temp_selected
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
                                        if not(selected.trapped) and not(selected.killed):
                                            haveSelected = True
                                            for x,y in selectedMoves:
                                                b.tiles[x][y].swap_highlight()
                                            selectedMoves = possible_moves(selected, b, players)
                                            for x,y in selectedMoves:
                                                b.tiles[x][y].swap_highlight()
                                        break
            if event:
                hud.event(event)
            
        # Clear the screen, update sprites, draw to screen
        screen.blit(background, (0,0))
        if mode in [4,5,6,7]:
            b.clear(screen, background)
            for p in players:
                p.pieces.clear(screen,background)
            if mode in [6,7]:
                marker.clear(screen, background)
            b.update()
            for p in players:
                p.pieces.update()
            if mode in [6,7]:
                marker.update()
            b.draw(screen)
            for i in range(len(players)):
                if i is not turnPlayer:
                    players[i].pieces.draw(screen)
            players[turnPlayer].pieces.draw(screen)
            if mode in [6,7]:
                marker.draw(screen)
        hud.paint()
        #screen.blit(titleImage, titleRect)
                    
        pygame.display.flip()
        
if __name__ == '__main__': main()
