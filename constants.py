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
PIECE_SIZE = 40
PIECE_START_X = BOARD_OFFSET_X - PIECE_SIZE
PIECE_START_Y = BOARD_OFFSET_Y

# Player constants
NUM_PLAYERS = 2 
