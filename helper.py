import pygame, os, sys
from pygame.locals import *
from constants import *      

# Determines if the game is over
def is_game_over(players, b):
    flags_captured = []
    pieces_disabled = []
    for i in range(NUM_PLAYERS):
        pieces_disabled.append(True)
        flags_captured.append(0)
    for i in range(len(players)):
        player = players[i]
        for piece in player.pieces:
            if piece.type == 'F' and piece.trapped:
                flags_captured[i] += 1
                #flag_pos.append((piece.x, piece.y))
            elif not(piece.killed):
                moves = possible_moves(piece, b, players)
                if len(moves) > 0:
                    pieces_disabled[i] = False
    if flags_captured[0] + flags_captured[2] is 2:
        return 'Blue'
    elif flags_captured[1] + flags_captured[3] is 2:
        return 'Red'
    if pieces_disabled[0] and pieces_disabled[2]:
        return 'Blue'
    elif pieces_disabled[1] and pieces_disabled[3]:
        return 'Red'
    return None
            

# Determines the outcome of combat between the pieces attacker and defender
def fight(attacker, defender):
    try:
        aType = int(attacker.type)
        dType = int(defender.type)
        if aType >= dType:
            return 1
        else:
            return 0
    except:
        if attacker.type is 'B':
            return 1
        elif attacker.type is 'S':
            if defender.type in ['F', 'S', '10', 'B']:
                return 1
            else:
                return 0
        elif attacker.type is 'F':
            return 0
        if defender.type is 'B':
            return 1
        elif defender.type is 'S':
            return 1
        elif defender.type is 'F':
            return 1
        return 1


# Returns all starting tiles for given color
def starting_tiles(color, b):
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

# Finds all available starting tiles for the selected piece
def starting_moves(selected, b, player):
    moves = []
    for i in range(4,11):
        if selected.color is 'red':
            moves.append((i,13))
            moves.append((i,12))
        elif selected.color is 'dred':
            moves.append((i,1))
            moves.append((i,2))
        elif selected.color is 'blue':
            moves.append((1,i))
            moves.append((2,i))
        elif selected.color is 'dblue':
            moves.append((13,i))
            moves.append((12,i))
    toRemove = []
    if player.color is selected.color:
        for i,j in moves:
            tileRect = b.tiles[i][j].rect
            if not b.is_legal(i,j):
                toRemove.append((i,j))
            else:
                for piece in player.pieces:
                    if piece.click_check(tileRect) is not None:
                        toRemove.append((i,j))
    for pos in toRemove:
        moves.remove(pos)
    return moves

# Checks if there is a piece from player p or their ally in the space (x,y)
def is_occupied(p, b, x, y, players):
    tileRect = b.tiles[x][y].rect
    redteam = ['red', 'dred']
    blueteam = ['blue', 'dblue']
    if p.color in redteam:
        for pl in players:
            if pl.color in redteam:
                for piece in pl.pieces:
                    collision = piece.click_check(tileRect)
                    if collision is not None:
                        return True
    elif p.color in blueteam:
        for pl in players:
            if pl.color in blueteam:
                for piece in pl.pieces:
                    collision = piece.click_check(tileRect)
                    if collision is not None:
                        return True
    return False
"""
    tileRect = b.tiles[x][y].rect
    for piece in p.pieces:
        collision = piece.click_check(tileRect)
        if collision is not None:
            return True
    return False
"""

# Checks if there is a piece from a player other than p in the space (x,y)
def is_occupied_excluding(p, players, b, x, y):
    tileRect = b.tiles[x][y].rect
    for pl in players:
        if pl.color is p.color:
            continue
        for piece in pl.pieces:
            collision = piece.click_check(tileRect)
            if collision is not None:
                return True
    return False
    
# Checks if there is a piece from an enemy player in the space (x,y)
def is_occupied_enemy(p, players, b, x, y):
    tileRect = b.tiles[x][y].rect
    redteam = ['red', 'dred']
    blueteam = ['blue', 'dblue']
    if p.color in redteam:
        for pl in players:
            if pl.color in blueteam:
                for piece in pl.pieces:
                    collision = piece.click_check(tileRect)
                    if collision is not None:
                        return True
    elif p.color in blueteam:
        for pl in players:
            if pl.color in redteam:
                for piece in pl.pieces:
                    collision = piece.click_check(tileRect)
                    if collision is not None:
                        return True
    return False

# Finds all possible moves for the selected piece
def possible_moves(selected, board, players):
    moves = []
    x = selected.x
    y = selected.y
    p = None
    for pl in players:
        if pl.color == selected.color:
            p = pl
    if p is None:
        print 'You are not a player in the game'
        sys.exit()
        
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
    #print 'is_legal: ' + str(board.is_legal(x,y+1)) + ', is_occupied: ' + str(is_occupied(p, board, x, y+1, players))
    if board.is_legal(x, y+1) and not(is_occupied(p, board, x, y+1, players)):
        if selected.type in ['B', 'F']:
            if not(is_occupied_excluding(p, players, board, x, y+1)):
                moves.append((x,y+1))
        else:
            #print 'Appending: (' + str(x) + ', ' + str(y+1) + ')'
            moves.append((x,y+1))
            
    # Append special moves for 2's
    if selected.type is '2':
        if not(is_occupied_excluding(p, players, board, x+1, y)) and not(is_occupied(p, board, x+1,y, players)) and board.is_legal(x+1, y):
            for i in range(x+2, BOARD_SIZE):
                if board.is_legal(i, y) and not(is_occupied(p, board, i, y, players)):
                    moves.append((i,y))
                    if is_occupied_excluding(p, players, board, i, y):
                        break
                else:
                    break
        if not(is_occupied_excluding(p, players, board, x-1, y)) and not(is_occupied(p, board,x-1, y, players)) and board.is_legal(x-1, y):
            for i in range(x-2, -1, -1):
                if board.is_legal(i,y) and not(is_occupied(p, board, i, y, players)):
                    moves.append((i,y))
                    if is_occupied_excluding(p, players, board, i, y):
                        break
                else:
                    break
        if not(is_occupied_excluding(p, players, board, x, y+1)) and not(is_occupied(p, board, x, y+1, players)) and board.is_legal(x, y+1):
            for i in range(y+2, BOARD_SIZE):
                if board.is_legal(x,i) and not(is_occupied(p, board, x, i, players)):
                    moves.append((x,i))
                    if is_occupied_excluding(p, players, board, x, i):
                        break
                else:
                    break
        if not(is_occupied_excluding(p, players, board, x, y-1)) and not(is_occupied(p, board, x, y-1, players)) and board.is_legal(x, y-1):
            for i in range(y-2, -1, -1):
                if board.is_legal(x,i) and not(is_occupied(p, board, x, i, players)):
                    moves.append((x,i))
                    if is_occupied_excluding(p, players, board, x, i):
                        break
                else:
                    break
                    
    # Append special moves for 6's
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
            
    # Append special moves for bombs
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
        """        
        pos = [(x-3,y),(x+3,y),(x,y-3),(x,y+3)]
        for i,j in pos:
            if not board.is_legal(i,j):
                continue
            tileRect = board.tiles[i][j].rect
            for p in players:
                if p.color is not selected.color:
                    for piece in p.pieces:
                        if piece.click_check(tileRect) is not None:
                            moves.append((i,j))
                            break
                            """
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

# Converts indices to pixel coordinates on the board
def getPos(x,y):
    i = BOARD_OFFSET_X + TILE_SIZE * x 
    j = BOARD_OFFSET_Y + TILE_SIZE * y 
    return (i,j)
    
def get_color_id(color):
    if color == 'red':
        return 0
    if color == 'blue':
        return 1
    if color == 'dred':
        return 2
    if color == 'dblue':
        return 3
    

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
