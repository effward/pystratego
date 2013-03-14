##########################################################################
## hud.py
##
## Layouts of all the different interfaces
##
## by Andrew Francis
##########################################################################
import pygame, threading, string
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
    """Pre-Lobby Interface"""
    menu = gui.App()
    menu.connect(gui.QUIT,menu.quit,None)
    
    main = gui.Container(width=500, height=400) 
    
    main.add(gui.Label("Select User", cls="h1"), 20, 20)


    my_input = gui.Input(value='New User', size=12)
    main.add(my_input, 40,80)
    my_list = gui.List(width=150, height=100)
    main.add(my_list, 250, 80)
    
    count = 1
    
    def remove_list_item(arg):
        """Removes selected list item"""
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
        """Adds new item to list with the value entered in the text box"""
        my_list.add(my_input.value,value=my_input.value)
        my_list.resize()
        my_list.repaint()
        users = open(USERS_FILE, 'a')
        users.write(my_input.value)
        users.write('\n')
        users.close()
        
    def select_user(arg):
        """Picks the selected username"""
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
    """Lobby Interface"""
    lobby = MyApp()
    lobby.connect(gui.QUIT,lobby.quit,None)
    
    main = gui.Container(width=1280, height=720) 
    
    def chat_message(_event,_widget,_code,a,b,c):
        t.tr()
        t.td(gui.Label(nick))
    
    main.add(gui.Label("Main Lobby", cls="h1"), 20, 20)
    
    t = gui.Table()
    box = gui.ScrollArea(t,800,550)
    main.add(box,20,60)
    
    box.connect(gui.CLICK, chat_message,1,2,3)
    
    lobby.init(main)
    return lobby
    
def load_loading_screen():
    """Loading Screen Interface"""
    screen = MyApp()
    screen.connect(gui.QUIT, screen.quit, None)
    
    main = gui.Container(width=500, height=400)
    
    main.add(gui.Label("Finding Available Games...", cls="h1"), 100, 100)
    
    screen.init(main)
    return screen
    
def load_game_lobby(server=False, games=[]):
    """Game Lobby interface"""
    menu = gui.App()
    menu.connect(gui.QUIT,menu.quit,None)
    
    main = gui.Container(width=500, height=400)
    
    main.add(gui.Label("Select Game", cls="h1"), 20, 20)

    my_list = gui.List(width=150, height=100)
    main.add(my_list, 250, 80)

    count = 1
    
    def clean_room_name(name):
        """Make the room name clean for XMPP rooms"""
        clean_name = ''
        name = name.lower()
        name_parts = name.split(' ')
        for i in range(len(name_parts)):
            for letter in name_parts[i]:
                if letter in string.ascii_lowercase:
                    clean_name += letter
            if i < len(name_parts)-1:
                clean_name += '_'
        return clean_name
            

    def add_list_item(arg):
        """Adds new item to list with the value entered in the text box"""
        room_name = clean_room_name(my_input.value)
        pygame.event.post(Event(NETWORK, msg='create_room', room=room_name))
        my_list.add(room_name,value=room_name)
        my_list.resize()
        my_list.repaint()
        FILE_LOCK.acquire()
        rooms = open(ROOMS_FILE, 'a')
        rooms.write(room_name)
        rooms.write('\n')
        rooms.close()
        FILE_LOCK.release()
        
    def select_room(arg):
        """Picks the highlighted room"""
        room_name = my_list.value
        if room_name:
            if server:
                pygame.event.post(Event(MODECHANGE, mode=1, room=room_name))
            else:
                pygame.event.post(Event(MODECHANGE, mode=3, room=room_name))
            
    def refresh_rooms(arg):
        """Requests a new list of available games"""
        if server:
            pygame.event.post(Event(MODECHANGE, mode=0))
        else:
            pygame.event.post(Event(NETWORK, msg='connected'))

    
    if server:
        for game in games:
            my_list.add(game, value=game)
    else:
        FILE_LOCK.acquire()
        rooms = open(ROOMS_FILE, 'r')
        for line in rooms:
            room = line.strip()
            if room:
                my_list.add(room, value=room)
        rooms.close()
        FILE_LOCK.release()
    
        my_input = gui.Input(value='New Game', size=12)
        main.add(my_input, 40,80)
        b = gui.Button("Create New Game", width=150)
        main.add(b, 40, 110)
        b.connect(gui.CLICK, add_list_item, None)
    
    b = gui.Button("Select", width=150)
    main.add(b, 250, 200)
    b.connect(gui.CLICK, select_room, None)
    
    b = gui.Button("Refresh", width=150)
    main.add(b, 250, 225)
    b.connect(gui.CLICK, refresh_rooms, None)
    
    menu.init(main)
    
    return menu
    
def load_loading_game():
    """Loading game interface"""
    screen = MyApp()
    screen.connect(gui.QUIT, screen.quit, None)
    
    main = gui.Container(width=500, height=400)
    
    main.add(gui.Label("Connecting to Game...", cls="h1"), 100, 100)
    
    screen.init(main)
    return screen
    
def load_pre_game_hud():
    """Pre-game interface"""
    hud = gui.App()
    hud.connect(gui.QUIT, hud.quit, None)
    
    main = gui.Container(width=1280, height=720)
    
    main.add(gui.Label("Choose Your Positions", cls="h1"), 20, 20)
    
    def add_ai_player(arg):
        pygame.event.post(Event(NETWORK, msg='add_ai'))
    
    b = gui.Button("Add AI-Controlled Bot", width=150)
    main.add(b, 20, 50)
    b.connect(gui.CLICK, add_ai_player, None)
    
    hud.init(main)
    return hud
    
def load_waiting_hud():
    """Waiting for game to start interface"""
    hud = gui.App()
    hud.connect(gui.QUIT, hud.quit, None)
    
    main = gui.Container(width=1280, height=720)
    
    main.add(gui.Label("Waiting for other players...", cls="h1"), 20, 20)
    
    def add_ai_player(arg):
        pygame.event.post(Event(NETWORK, msg='add_ai'))
    
    b = gui.Button("Add AI-Controlled Bot", width=150)
    main.add(b, 20, 50)
    b.connect(gui.CLICK, add_ai_player, None)
    
    hud.init(main)
    return hud
    
def load_game_hud(server=False):
    """In-game interface"""
    hud = gui.App()
    hud.connect(gui.QUIT, hud.quit, None)
    
    main = gui.Container(width=1280, height=720)
    
    if server:
        def back_to_lobby(arg):
            pygame.event.post(Event(MODECHANGE, mode=0))
        
        b = gui.Button("Back to Lobby", width=150)
        main.add(b, 20, 100)
        b.connect(gui.CLICK, back_to_lobby, None)
    
    hud.init(main)
    return hud
    
def load_post_game_hud(result):
    """Post-game interface, displays result"""
    hud = gui.App()
    hud.connect(gui.QUIT, hud.quit, None)
    
    main = gui.Container(width=1280, height=720)
    win_str = result + " Team wins!"
    main.add(gui.Label(win_str, cls="h1"), 20, 40)
    
    def back_to_lobby(arg):
        pygame.event.post(Event(MODECHANGE, mode=8))
    
    b = gui.Button("Back to Lobby", width=150)
    main.add(b, 20, 100)
    b.connect(gui.CLICK, back_to_lobby, None)
    
    hud.init(main)
    return hud
    
def load_quitting_game_hud():
    """Quitting game interface"""
    hud = gui.App()
    hud.connect(gui.QUIT, hud.quit, None)
    
    main = gui.Container(width=1280, height=720)
    main.add(gui.Label("Quitting Game...", cls="h1"), 100, 100)
    
    hud.init(main)
    return hud
    
def load_hud(mode, text=None):
    """Loads the correct interface corresponding to mode"""
    if mode is 0:
        return load_pre_lobby()
    elif mode is 1:
        #return load_lobby()
        return load_loading_screen()
    elif mode is 2:
        return load_game_lobby()
    elif mode is 3:
        return load_loading_game()
    elif mode is 4:
        return load_pre_game_hud()
    elif mode is 5:
        return load_waiting_hud()
    elif mode is 6:
        return load_game_hud()
    elif mode is 7:
        return load_post_game_hud(text)
    elif mode is 8:
        return load_loading_screen()
        
def load_server_hud(mode, text=None, games=[]):
    """Loads the correct interface according to the server mode"""
    if mode is 0:
        return load_game_lobby(server=True, games=games)
    if mode is 1:
        return load_game_hud(server=True)