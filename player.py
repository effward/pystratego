import pygame, helper, random, board
from pygame.event import Event
from helper import *
from constants import *

class Piece(pygame.sprite.Sprite):
    def __init__(self, color, type, x, y, server, pregame=False):
        # Call Sprite initializer
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
        # Position on the board [0...14], -1 means pre-placement, -2 means captured
        self.x = x
        self.y = y
        self.x_velocity = 0
        self.y_velocity = 0
        self.trapped = False
        self.killed = False
        self.server = server
        
    def click_check(self, mouseRect):
        if mouseRect.colliderect(self.rect):
            return self    
        return None

    def move(self, x, y):
        #x1,y1 = self.rect.center
        #x2,y2 = helper.getPos(x,y)
        #self.x_velocity = (x2 - x1) / 100
        #self.y_velocity = (y2 - y1) / 100
        if self.type == '2':
            print "Before: " + str(self.x) + ' ' + str(self.y)
        self.x = x
        self.y = y
        if self.type == '2':
            print "Moving piece: " + self.color + ' ' + self.type + ' ' + str(self.x) + ' ' + str(self.y)
        self.rect.center = helper.getPos(x,y)
        
    def off_board(self):
        if self.x < 0 or self.x >= BOARD_SIZE or self.y < 0 or self.y >= BOARD_SIZE:
            return True
        return False
        
    """    
    def update(self):
        if self.x > 0 and self.y > 0:
            targetPos =  (self.x * const.TILE_SIZE + const.BOARD_OFFSET_X, self.y * const.TILE_SIZE + const.BOARD_OFFSET_Y)
            if self.rect.center is not targetPos:
                self.rect.move_ip((self.x_velocity, self.y_velocity))
            else:
                self.x_velocity = 0
                self.y_velocity = 0
        """
        

class Player:
    def __init__(self, b, color, remote=False, server=False, ai=False):
        self.color = color
        #self.board = b
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
            if remote:
                type = 'U'
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
                
            """
        self.pieces.add(Piece(color, '2', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 0)))
        self.pieces.add(Piece(color, '2', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 1)))
        self.pieces.add(Piece(color, '3', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 2)))
        self.pieces.add(Piece(color, '4', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 3)))
        self.pieces.add(Piece(color, '5', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 4)))
        self.pieces.add(Piece(color, '6', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 5)))
        self.pieces.add(Piece(color, '7', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 6)))
        self.pieces.add(Piece(color, '8', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 7)))
        self.pieces.add(Piece(color, '9', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 8)))
        self.pieces.add(Piece(color, '10', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 9)))
        self.pieces.add(Piece(color, 'S', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 10)))
        self.pieces.add(Piece(color, 'F', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 11)))
        self.pieces.add(Piece(color, 'B', (const.PIECE_START_X, const.PIECE_START_Y + const.PIECE_SIZE * 12)))
        """
        
    def random_start(self, b):
        for piece in self.pieces:
            moves = starting_moves(piece, b, self)
            x,y = moves[random.randint(0, len(moves)-1)]
            piece.move(x,y)
                    
    def ready(self):
        for piece in self.pieces:
            if piece.off_board():
                if self.server:
                    print 'Piece: ' + piece.color + ' ' + piece.type + ' (' + str(piece.x) + ', ' + str(piece.y) + ')'
                return False
        return True
        
    def kill(self, piece, killer):
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
        
