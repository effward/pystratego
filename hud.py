import pygame, threading
from pgu import gui
from tempfile import mkstemp
from shutil import move
from os import remove, close
from pygame.event import Event
from constants import *

class MyApp(gui.App):
	def __init__(self):
		gui.App.__init__(self)
		
	def event(self, ev):
		if ev.type == CHATMESSAGE:
			print '********************************************************Event : ' + str(ev)
			e = pygame.event.Event(ev.type, nick=ev.nick)
			gui.Widget.send(self, e.type, e)
		#gui.App.event(self,ev)

def load_pre_lobby():
	menu = gui.App()
	menu.connect(gui.QUIT,menu.quit,None)
	
	main = gui.Container(width=500, height=400) #, background=(220, 220, 220) )
	
	main.add(gui.Label("Select User", cls="h1"), 20, 20)


	my_input = gui.Input(value='New User', size=12)
	main.add(my_input, 40,80)
	my_list = gui.List(width=150, height=100)
	main.add(my_list, 250, 80)
	
	count = 1
	
	def remove_list_item(arg):
		v = my_list.value
		if v:
			item = v
			my_list.remove(item)
			my_list.resize()
			my_list.repaint()
		fh, abs_path = mkstemp()
		new_users = open(abs_path, 'w')
		users = open(USERS_FILE)
		for line in users:
			if line and not(line.strip()  == v):
				new_users.write(line)
		new_users.close()
		close(fh)
		users.close()
		remove(USERS_FILE)
		move(abs_path, USERS_FILE)

	def add_list_item(arg):
		my_list.add(my_input.value,value=my_input.value)
		my_list.resize()
		my_list.repaint()
		users = open(USERS_FILE, 'a')
		users.write(my_input.value)
		users.write('\n')
		users.close()
		
	def select_user(arg):
		user = my_list.value
		if user:
			pygame.event.post(Event(MODECHANGE, mode=1, nick=user))
		
	users = open(USERS_FILE, 'r')
	for line in users:
		user = line.strip()
		if user:
			my_list.add(user, value=user)
	users.close()
	
	b = gui.Button("Add New User", width=150)
	main.add(b, 40, 110)
	b.connect(gui.CLICK, add_list_item, None)

	b = gui.Button("Remove Selected", width=150)
	main.add(b, 40, 140)
	b.connect(gui.CLICK, remove_list_item, None)
	
	b = gui.Button("Select", width=150)
	main.add(b, 250, 200)
	b.connect(gui.CLICK, select_user, None)
	
	menu.init(main)
	
	return menu
	

def load_lobby():
	lobby = MyApp()
	lobby.connect(gui.QUIT,lobby.quit,None)
	
	main = gui.Container(width=1280, height=720) 
	
	def chat_message(_event,_widget,_code,a,b,c):
		print '***********************************************************************'
		print 'STAR STAR'
		print '***********************************************************************'
		print _event
		t.tr()
		t.td(gui.Label(nick))
	
	main.add(gui.Label("Main Lobby", cls="h1"), 20, 20)
	
	t = gui.Table()
	box = gui.ScrollArea(t,800,550)
	main.add(box,20,60)
	
	box.connect(CHATMESSAGE, chat_message,1,2,3)
	
	lobby.init(main)
	return lobby
	
def load_game_lobby():
	menu = gui.App()
	menu.connect(gui.QUIT,menu.quit,None)
	
	main = gui.Container(width=500, height=400) #, background=(220, 220, 220) )
	
	main.add(gui.Label("Select Game", cls="h1"), 20, 20)


	my_input = gui.Input(value='New Game', size=12)
	main.add(my_input, 40,80)
	my_list = gui.List(width=150, height=100)
	main.add(my_list, 250, 80)
	
	count = 1
	
	def remove_list_item(arg):
		v = my_list.value
		if v:
			item = v
			my_list.remove(item)
			my_list.resize()
			my_list.repaint()
		fh, abs_path = mkstemp()
		new_users = open(abs_path, 'w')
		users = open(USERS_FILE)
		for line in users:
			if line and not(line.strip()  == v):
				new_users.write(line)
		new_users.close()
		close(fh)
		users.close()
		remove(USERS_FILE)
		move(abs_path, USERS_FILE)

	def add_list_item(arg):
		my_list.add(my_input.value,value=my_input.value)
		my_list.resize()
		my_list.repaint()
		users = open(USERS_FILE, 'a')
		users.write(my_input.value)
		users.write('\n')
		users.close()
		
	def select_user(arg):
		user = my_list.value
		if user:
			pygame.event.post(Event(MODECHANGE, mode=1, nick=user))
		
	users = open(USERS_FILE, 'r')
	for line in users:
		user = line.strip()
		if user:
			my_list.add(user, value=user)
	users.close()
	
	b = gui.Button("Create New Game", width=150)
	main.add(b, 40, 110)
	b.connect(gui.CLICK, add_list_item, None)
	
	b = gui.Button("Select", width=150)
	main.add(b, 250, 200)
	b.connect(gui.CLICK, select_user, None)
	
	menu.init(main)
	
	return menu
	
def load_hud(mode):
	if mode is 0:
		return load_pre_lobby()
	elif mode is 1:
		return load_lobby()
	elif mode is 2:
		return load_game_lobby()