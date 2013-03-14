##########################################################################
## player.py
##
## Stratego Piece, Player, and AIPlayer classes, used to represent the players and their pieces in a game of Ultimate Stratego.
##
## by Andrew Francis
##########################################################################
import pygame, helper, random, board
from pygame.event import Event
from helper import *
from constants import *

# A single piece controlled by a player
class Piece(pygame.sprite.Sprite):
    def __init__(self, color, type, x, y, server, pregame=False):
        # Call Sprite initializer if gui is being displayed
        if server:
            self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        else:
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = helper.load_image('piece_' + color + type + '.bmp', -1)
        i,j = helper.getPos(x,y)
        if pregame and color == 'red':
            j = j + 20
        elif pregame and color == 'dred':
            j = j - 20
        self.rect.center = (i,j)
        self.type = type
        self.color = color
        self.x = x
        self.y = y
        self.x_velocity = 0
        self.y_velocity = 0
        self.trapped = False
        self.killed = False
        self.server = server
        
    def click_check(self, mouseRect):
        """Returns itself if mouseRect intersects with this tile, null otherwise"""
        if mouseRect.colliderect(self.rect):
            return self    
        return None

    def move(self, x, y):
        """Moves this piece to board square (x,y)"""
        self.x = x
        self.y = y
        self.rect.center = helper.getPos(x,y)
        
    def off_board(self):
        """Returns True if this piece is not on a legal square, flase otherwise"""
        if self.x < 0 or self.x >= BOARD_SIZE or self.y < 0 or self.y >= BOARD_SIZE:
            return True
        return False
        

# A single player in a game of Ultimate Stratego
class Player:
    def __init__(self, b, color, remote=False, server=False, ai=False):
        self.color = color
        self.kills = 0
        self.nick = None
        self.nickpos = None
        self.nick_plain = ''
        self.is_ai = ai
        self.server = server
        if server:
            self.pieces = []
            for i in range(len(PIECE_TYPES)):
                if self.color == 'red':
                    self.pieces.append(Piece(color, PIECE_TYPES[i], i+1, BOARD_SIZE, server))
                elif self.color == 'blue':
                    self.pieces.append(Piece(color, PIECE_TYPES[i], -1, i+1, server))
                elif self.color == 'dred':
                    self.pieces.append(Piece(color, PIECE_TYPES[i], i+1, -1, server))
                elif self.color == 'dblue':
                    self.pieces.append(Piece(color, PIECE_TYPES[i], BOARD_SIZE, i+1, server))
        else:
            self.pieces = pygame.sprite.Group()
            if remote: # if this player is remote
                type = 'U' # All of his pieces are unknown
                for i in range(len(PIECE_TYPES)):
                    if self.color == 'red':
                        self.pieces.add(Piece(color, type, 1, BOARD_SIZE, server))
                    elif self.color == 'blue':
                        self.pieces.add(Piece(color, type, -1, 1, server))
                    elif self.color == 'dred':
                        self.pieces.add(Piece(color, type, 1, -1, server))
                    elif self.color == 'dblue':
                        self.pieces.add(Piece(color, type, BOARD_SIZE, 1, server))
            else:
                for i in range(len(PIECE_TYPES)):
                    if self.color == 'red':
                        self.pieces.add(Piece(color, PIECE_TYPES[i], i+1, BOARD_SIZE, server, True))
                    elif self.color == 'blue':
                        self.pieces.add(Piece(color, PIECE_TYPES[i], -2, i+1, server))
                    elif self.color == 'dred':
                        self.pieces.add(Piece(color, PIECE_TYPES[i], i+1, -1, server, True))
                    elif self.color == 'dblue':
                        self.pieces.add(Piece(color, PIECE_TYPES[i], BOARD_SIZE + 1, i+1, server))

        
    def random_start(self, b):
        """Places all of this player's pieces in random starting locations"""
        for piece in self.pieces:
            moves = starting_moves(piece, b, self)
            x,y = moves[random.randint(0, len(moves)-1)]
            piece.move(x,y)
                    
    def ready(self):
        """Returns true if all of this player's pieces have been placed, false otherwise"""
        for piece in self.pieces:
            if piece.off_board():
                if self.server:
                    print 'Piece: ' + piece.color + ' ' + piece.type + ' (' + str(piece.x) + ', ' + str(piece.y) + ')'
                return False
        return True
        
    def kill(self, piece, killer):
        """Kills piece if it belongs to this player, and moves it to the killer's capture area"""
        if not(piece.color == self.color):
            print "Can only kill pieces belonging to this player"
            return
        if piece.type == 'F':
            piece.trapped = True
            x,y = STOCKADE_POS[get_color_id(killer.color)]
            piece.move(x,y)
        else:
            piece.killed = True
            if killer.color == 'red':
                piece.move(killer.kills % BOARD_SIZE, BOARD_SIZE + (killer.kills / BOARD_SIZE))
            elif killer.color == 'blue':
                piece.move(-1 - (killer.kills / BOARD_SIZE), killer.kills % BOARD_SIZE)
            elif killer.color == 'dred':
                piece.move(killer.kills % BOARD_SIZE, -1 - (killer.kills / BOARD_SIZE))
            elif killer.color == 'dblue':
                piece.move(BOARD_SIZE + (killer.kills / BOARD_SIZE), killer.kills % BOARD_SIZE)
            killer.kills += 1
            
            
# A basic AI Player
class AIPlayer(Player):
    def __init__(self, b, color, game_name, gui):
        self.game_name = game_name
        self.gui = gui
        if gui:
            Player.__init__(self, b, color, server=False, ai=True)
        else:
            Player.__init__(self, b, color, server=True, ai=True)
        self.nick_plain = 'pyStratego Bot #' + str(random.randint(0, 10000))
        self.start(b)
        
    def start(self, b):
        """Places the AI player's pieces randomly"""
        moves = []
        for piece in self.pieces:
            avail_moves = starting_moves(piece, b, self)
            x,y = avail_moves[random.randint(0, len(avail_moves)-1)]
            piece.move(x,y)
            move = ['-1', piece.color, piece.type, str(-1), str(-1), str(x), str(y)]
            moves.append(move)
        for piece in self.pieces:
            piece.move(-1, -1)
        for move in moves:
            pygame.event.post(Event(NETWORK, msg='check_move', game_name=self.game_name, move=move))
            
    def move(self, b, players, turn):
        """Picks a piece at random and moves it in to a random position"""
        moves = []
        if self.gui:
            for k in range(10000):
                n = random.randint(0, len(self.pieces)-1)
                for idx,piece in enumerate(iter(self.pieces)):
                    if idx is n:
                        break
                if not(piece.killed or piece.trapped):
                    moves = possible_moves(piece, b, players)
                    if len(moves) > 0:
                        break
        else:
            for k in range(10000):
                piece = self.pieces[random.randint(0, len(self.pieces)-1)]
                if not(piece.killed or piece.trapped):
                    moves = possible_moves(piece, b, players)
                    if len(moves) > 0:
                        break
        if len(moves) > 0:
            x,y = moves[random.randint(0, len(moves)-1)]
            move = [str(turn), piece.color, piece.type, str(piece.x), str(piece.y), str(x), str(y)]
            pygame.event.post(Event(NETWORK, msg='check_move', game_name=self.game_name, move=move))
        
