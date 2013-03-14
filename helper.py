##########################################################################
## helper.py
##
## Contains several misc. helper classes.
##
## by Andrew Francis
##########################################################################
import pygame, os, sys
from pygame.locals import *
from constants import *      

def is_game_over(players, b):
    """Determines if the game is over"""
    flags_captured = []
    pieces_disabled = []
    # Initialize lists
    for i in range(NUM_PLAYERS):
        pieces_disabled.append(True)
        flags_captured.append(0)
    for i in range(len(players)):
        player = players[i]
        # Go through each player's pieces
        for piece in player.pieces:
            # and check if the flag is trapped
            if piece.type == 'F' and piece.trapped:
                flags_captured[i] += 1
            # and check, if the piece is alive, if it can move
            elif not(piece.killed):
                moves = possible_moves(piece, b, players)
                if len(moves) > 0:
                    pieces_disabled[i] = False
    # if both red flags are captured, blue wins
    if flags_captured[0] + flags_captured[2] is 2:
        return 'Blue'
    # if both blue flags are captured, red wins
    elif flags_captured[1] + flags_captured[3] is 2:
        return 'Red'
    # if none of red's pieces can move, blue wins
    if pieces_disabled[0] and pieces_disabled[2]:
        return 'Blue'
    # if none of blue's pieces can move, red wins
    elif pieces_disabled[1] and pieces_disabled[3]:
        return 'Red'
    return None
            

def fight(attacker, defender):
    """Determines the outcome of combat between the pieces attacker and defender
        Returns 1 if attacker wins, 0 if defender wins"""
    try:
        # if the pieces are numbers, higher number wins, attacker wins ties
        aType = int(attacker.type)
        dType = int(defender.type)
        if aType >= dType:
            return 1
        else:
            return 0
    except:
        if attacker.type is 'B': # Bombs
            return 1 # kill everything
        elif attacker.type is 'S': # Spies
            if defender.type in ['F', 'S', '10', 'B']: 
                return 1 # kill flags, spies, marshals, and bombs
            else:
                return 0 # die otherwise
        elif attacker.type is 'F': # Flags
            return 0 # shouldn't be able to attack
        if defender.type is 'B': # Bombs
            return 1 # always lose
        elif defender.type is 'S': # Spies
            return 1 # always lose
        elif defender.type is 'F': # Flags
            return 1 # always lose
        return 1


def starting_tiles(color, b):
    """Returns all starting tiles for given color"""
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

    
def starting_moves(selected, b, player):
    """Finds all available starting tiles for the selected piece"""
    moves = starting_tiles(selected.color, b)
    toRemove = []
    # mark tiles for removal that already have pieces on them
    if player.color is selected.color:
        for i,j in moves:
            tileRect = b.tiles[i][j].rect
            for piece in player.pieces:
                if piece.click_check(tileRect) is not None:
                    toRemove.append((i,j))
    # remove marked tiles
    for pos in toRemove:
        moves.remove(pos)
    return moves


def is_occupied(p, b, x, y, players):
    """Checks if there is a piece from player p or their ally in the space (x,y)"""
    tileRect = b.tiles[x][y].rect
    if p.color in RED_TEAM:
        for pl in players:
            if pl.color in RED_TEAM:
                for piece in pl.pieces:
                    collision = piece.click_check(tileRect)
                    if collision is not None:
                        return True
    elif p.color in BLUE_TEAM:
        for pl in players:
            if pl.color in BLUE_TEAM:
                for piece in pl.pieces:
                    collision = piece.click_check(tileRect)
                    if collision is not None:
                        return True
    return False


def is_occupied_excluding(p, players, b, x, y):
    """Checks if there is a piece from a player other than p in the space (x,y)"""
    tileRect = b.tiles[x][y].rect
    for pl in players:
        if pl.color is p.color:
            continue
        for piece in pl.pieces:
            collision = piece.click_check(tileRect)
            if collision is not None:
                return True
    return False
    

def is_occupied_enemy(p, players, b, x, y):
    """Checks if there is a piece from an enemy player in the space (x,y)"""
    tileRect = b.tiles[x][y].rect
    if p.color in RED_TEAM:
        for pl in players:
            if pl.color in BLUE_TEAM:
                for piece in pl.pieces:
                    collision = piece.click_check(tileRect)
                    if collision is not None:
                        return True
    elif p.color in BLUE_TEAM:
        for pl in players:
            if pl.color in RED_TEAM:
                for piece in pl.pieces:
                    collision = piece.click_check(tileRect)
                    if collision is not None:
                        return True
    return False


def possible_moves(selected, board, players):
    """Finds all possible moves for the selected piece"""
    moves = []
    x = selected.x
    y = selected.y
    p = None
    for pl in players:
        if pl.color == selected.color:
            p = pl
    if p is None:
        print 'You are not a player in the game'
        pygame.event.post(Event(QUIT))
        
    # Append the 4 basic move directions to the list of moves    
    if board.is_legal(x-1, y) and not(is_occupied(p, board, x-1, y, players)):
        if selected.type in ['B', 'F']:
            if not(is_occupied_excluding(p, players, board, x-1, y)):
                moves.append((x-1,y))
        else:
            moves.append((x-1,y))
    if board.is_legal(x, y-1) and not(is_occupied(p, board, x, y-1, players)):
        if selected.type in ['B', 'F']:
            if not(is_occupied_excluding(p, players, board, x, y-1)):
                moves.append((x,y-1))
        else:
            moves.append((x,y-1))
    if board.is_legal(x+1, y) and not(is_occupied(p, board, x+1, y, players)):
        if selected.type in ['B', 'F']:
            if not(is_occupied_excluding(p, players, board, x+1, y)):
                moves.append((x+1,y))
        else:
            moves.append((x+1,y))
    if board.is_legal(x, y+1) and not(is_occupied(p, board, x, y+1, players)):
        if selected.type in ['B', 'F']:
            if not(is_occupied_excluding(p, players, board, x, y+1)):
                moves.append((x,y+1))
        else:
            moves.append((x,y+1))
            
    # Append special moves for 2's, 2's can move any distance in a straight line
    if selected.type is '2':
        if board.is_legal(x+1, y) and not(is_occupied_excluding(p, players, board, x+1, y)) and not(is_occupied(p, board, x+1,y, players)):
            for i in range(x+2, BOARD_SIZE):
                if board.is_legal(i, y) and not(is_occupied(p, board, i, y, players)):
                    moves.append((i,y))
                    if is_occupied_excluding(p, players, board, i, y):
                        break
                else:
                    break
        if board.is_legal(x-1, y) and not(is_occupied_excluding(p, players, board, x-1, y)) and not(is_occupied(p, board,x-1, y, players)):
            for i in range(x-2, -1, -1):
                if board.is_legal(i,y) and not(is_occupied(p, board, i, y, players)):
                    moves.append((i,y))
                    if is_occupied_excluding(p, players, board, i, y):
                        break
                else:
                    break
        if board.is_legal(x, y+1) and not(is_occupied_excluding(p, players, board, x, y+1)) and not(is_occupied(p, board, x, y+1, players)):
            for i in range(y+2, BOARD_SIZE):
                if board.is_legal(x,i) and not(is_occupied(p, board, x, i, players)):
                    moves.append((x,i))
                    if is_occupied_excluding(p, players, board, x, i):
                        break
                else:
                    break
        if board.is_legal(x, y-1) and not(is_occupied_excluding(p, players, board, x, y-1)) and not(is_occupied(p, board, x, y-1, players)):
            for i in range(y-2, -1, -1):
                if board.is_legal(x,i) and not(is_occupied(p, board, x, i, players)):
                    moves.append((x,i))
                    if is_occupied_excluding(p, players, board, x, i):
                        break
                else:
                    break
                    
    # Append special moves for 6's, 6's can move 2 squares in any direction
    elif selected.type is '6':
        extraMoves = []
        for i,j in moves:
            if is_occupied_excluding(p, players, board, i, j) or is_occupied(p, board, i, j, players):
                continue
            if (i-1 is not x or j is not y) and board.is_legal(i-1, j) and not(is_occupied(p, board, i-1, j, players)):
                if extraMoves.count((i-1,j)) is 0:
                    extraMoves.append((i-1,j))
            if (i is not x or j-1 is not y) and board.is_legal(i, j-1) and not(is_occupied(p, board, i, j-1, players)):
                if extraMoves.count((i,j-1)) is 0:
                    extraMoves.append((i,j-1))
            if (i+1 is not x or j is not y) and board.is_legal(i+1, j) and not(is_occupied(p, board, i+1, j, players)):
                if extraMoves.count((i+1,j)) is 0:
                    extraMoves.append((i+1,j))
            if (i is not x or j+1 is not y) and board.is_legal(i, j+1) and not(is_occupied(p, board, i, j+1, players)):
                if extraMoves.count((i,j+1)) is 0:
                    extraMoves.append((i, j+1))
        for move in extraMoves:
            moves.append(move)
            
    # Append special moves for bombs, bombs can shoot over 2 squares if the 3rd is occupied by an enemy piece
    elif selected.type is 'B':
        for i in range(x+1, x+4):
            if not (board.is_legal(i,y) or board.is_legal_lake(i,y)):
                break
            if not(is_occupied_excluding(p, players, board, i, y)) and not(is_occupied(p, board, i,y, players)):
                continue
            elif is_occupied_excluding(p, players, board, i, y) and i == x+3:
                moves.append((i,y))
            else:
                    break
        for i in range(x-1, x-4, -1):
            if not(board.is_legal(i,y) or board.is_legal_lake(i,y)):
                break
            if not(is_occupied_excluding(p, players, board, i, y)) and not(is_occupied(p, board, i,y, players)):
                continue
            elif is_occupied_excluding(p, players, board, i, y) and i == x-3:
                moves.append((i,y))
            else:
                    break
        for i in range(y+1, y+4):
            if not(board.is_legal(x,i) or board.is_legal_lake(x,i)):
                break
            if not(is_occupied_excluding(p, players, board, x, i)) and not(is_occupied(p, board, x,i, players)):
                continue
            elif is_occupied_excluding(p, players, board, x, i) and i == y+3:
                moves.append((x,i))
            else:
                    break
        for i in range(y-1, y-4, -1):
            if not(board.is_legal(x,i) or board.is_legal_lake(x,i)):
                break
            if not(is_occupied_excluding(p, players, board, x, i)) and not(is_occupied(p, board, x,i, players)):
                continue
            elif is_occupied_excluding(p, players, board, x, i) and i == y-3:
                moves.append((x,i))
            else:
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


def getPos(x,y):
    """Converts indices to pixel coordinates on the board"""
    i = BOARD_OFFSET_X + TILE_SIZE * x 
    j = BOARD_OFFSET_Y + TILE_SIZE * y 
    return (i,j)
    
def get_color_id(color):
    """Returns the id number of the given team color"""
    if color == 'red':
        return 0
    if color == 'blue':
        return 1
    if color == 'dred':
        return 2
    if color == 'dblue':
        return 3
    
def render_nick(font, nick, color):
    """Renders the given nickname into a pygame font object to be drawn to the screen"""
    if color in ['red', 'dred']:
        nick_text = font.render(nick, 1, (90, 10, 10))
    if color in ['blue', 'dblue']:
        nick_text = font.render(nick, 1, (10, 10, 90))
    if color == 'red':
        nick_pos = nick_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - (BOARD_OFFSET_Y - 65)))
    elif color == 'blue':
        nick_pos = nick_text.get_rect(right=BOARD_OFFSET_X - 60, centery=SCREEN_HEIGHT/2)
    elif color == 'dred':
        nick_pos = nick_text.get_rect(center=(SCREEN_WIDTH/2, BOARD_OFFSET_Y - 65))
    elif color == 'dblue':
        nick_pos = nick_text.get_rect(left=SCREEN_WIDTH - (BOARD_OFFSET_X - 60), centery=SCREEN_HEIGHT/2)
    return nick_text, nick_pos


def load_image(file_name, colorkey=None):
    """Loads image with file name: file_name, if colorkey is specified
    all pixels that are the same color as the specified colorkey will be
    rendered as invisible
    
    From Pygame tutorial"""
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
    """Loads sound with file name: file_name
    
    From Pygame Tutorial"""
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