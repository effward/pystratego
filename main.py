import pygame, sys, random, os
import 'helper.py'

def main():
	pygame.init()
	random.seed()

	size = width, height = 1280, 720
	black = 0, 0, 0

	screen = pygame.display.set_mode(size)
	pygame.display.set_caption('pyStratego')
	
	background, background_rect = load_image("bg.bmp")
	screen.blit(background, (0,0))