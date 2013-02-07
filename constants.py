import threading
from pygame.locals import *

# Meta constants
SERVER_JID_PATTERN = '%s@pystratego.andrew-win7'
ROOM_JID_PATTERN = '%s@stratego.andrew-win7'
LOBBY_JID = 'lobby@stratego.andrew-win7'
USERS_FILE = 'users.txt'
ROOMS_FILE = 'rooms.txt'
MODECHANGE = USEREVENT
CHATMESSAGE = USEREVENT+1
NETWORK = USEREVENT+2
AI = USEREVENT+3

# Screen constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT

# Board constants
TILE_SIZE = 40
BOARD_SIZE = 15
BOARD_OFFSET_X = (SCREEN_WIDTH - (TILE_SIZE * BOARD_SIZE)) / 2 + TILE_SIZE/2
BOARD_OFFSET_Y = (SCREEN_HEIGHT - (TILE_SIZE * BOARD_SIZE)) / 2 + TILE_SIZE/2

# Piece constants
PIECE_TYPES = ['2','2','3','4','5','6','7','8','9','10','S','F','B']
PIECE_SIZE = 40
PIECE_START_X = BOARD_OFFSET_X - (PIECE_SIZE + PIECE_SIZE / 2)
PIECE_START_Y = BOARD_OFFSET_Y + PIECE_SIZE / 2

# Player constants
NUM_PLAYERS = 4
PLAYER_COLORS = ['red', 'blue', 'dred', 'dblue']
STOCKADE_POS = [(7,13),(1,7),(7,1),(13,7)]

# Threading
CHAT_QUEUE_LOCK = threading.Lock()
MOVE_QUEUE_LOCK = threading.Lock()
MOVE_QUEUE = []
FILE_LOCK = threading.Lock()
