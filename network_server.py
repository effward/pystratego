import logging, sys, threading, pygame

from sleekxmpp.componentxmpp import ComponentXMPP
from constants import *
from pygame.event import Event
from pygame.locals import *

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

class EchoComponent (ComponentXMPP, threading.Thread):
    def __init__(self, jid, secret, server, port, lobby, nick, target_jid, target_node='', get=''):
        ComponentXMPP.__init__(self, jid, secret, server, port)
        threading.Thread.__init__(self)
        
        logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
                        
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('old_0004')
        self.register_plugin('xep_0045') # Multi-User Chat
        self.register_plugin('xep_0199') # XMPP Ping
        
        self.lobby = lobby
        self.rooms = {}
        self.room_ids = {}
        self.nick = nick
        self.get = get
        self.target_jid = target_jid
        self.target_node = target_node
        
        # Values to control which disco entities are reported
        self.info_types = ['', 'all', 'info', 'identities', 'features']
        self.identity_types = ['', 'all', 'info', 'identities']
        self.feature_types = ['', 'all', 'info', 'features']
        self.items_types = ['', 'all', 'items']
        
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("groupchat_message", self.muc_message)
        self.add_event_handler("message", self.message)
        self.add_event_handler("broadcast", self.broadcast)
        self.add_event_handler("send_move", self.send_move)
        
        self.start()
        
    def run(self):
        if self.connect():
            self.process(block=True)
            print("done")
        else:
            print("Unable to Connect.")
            
    def session_start(self, event):
        #logging.debug('sending presence')
        
        # Join the lobby
        self['xep_0045'].joinMUC(self.lobby, self.nick, password='pystratego', wait=True, pfrom=SERVER_JID_PATTERN % 'lobby')
        
        if self.get in self.info_types:
            info = self['xep_0030'].get_info(jid=self.target_jid, node=self.target_node, block=True, ifrom=SERVER_JID_PATTERN % 'lobby')
        if self.get in self.items_types:
            items = self['xep_0030'].get_items(jid=self.target_jid, node=self.target_node, block=True, ifrom=SERVER_JID_PATTERN % 'lobby')
        else:
            logging.error("Invalid disco request type.")
            self.disconnect()
            return
        
        # Clean up left over rooms from crash, etc.
        if self.get in self.items_types:
            print('Items:')
            for item in items['disco_items']['items']:
                print('  - %s' % str(item))
                self['xep_0045'].destroy(item[0], ifrom=SERVER_JID_PATTERN % item[2])
                
    def broadcast(self, move_data):
        room, body = move_data
        self.send_message(mto=ROOM_JID_PATTERN % room, mbody=body, mtype='groupchat', mfrom=SERVER_JID_PATTERN % room)
        
    def send_move(self, move_data):
        room, jid, body = move_data
        print 'sending message to: ' + jid
        self.send_message(mto=jid, mbody=body, mtype='normal', mfrom=SERVER_JID_PATTERN % room)
                
    def muc_message(self, msg):
        if msg['mucnick'] != self.nick and self.nick in msg['body']:
            print '********' + msg['from'].bare + '**************'
            self.send_message(mto=msg['from'].bare, mbody="I heard that, %s." % msg['mucnick'], mtype='groupchat')
            
    def _create_room(self, room, nick):
        self.rooms[room] = [(nick,0)]
        self.room_ids[room] = 1
        print '****************************************'
        print self.rooms
        self['xep_0045'].joinMUC(ROOM_JID_PATTERN % room, self.nick, wait=True, pfrom=SERVER_JID_PATTERN % room)
        self['xep_0045'].configureRoom(ROOM_JID_PATTERN % room, ifrom=SERVER_JID_PATTERN % room)
        pygame.event.post(Event(NETWORK, msg='create_game', game_name=room))
    
    def message(self, message):
        if message['type'] in ('chat', 'normal'):
            body = message['body'].split(':')
            if len(body) > 1:
                command = body[0].strip()
                if command == 'CREATE':
                    room = body[1].strip()
                    self._create_room(room, message['nick'])
                    message.reply("CREATE: " + room + ": SUCCESS").send()
                if command == 'JOIN':
                    room = body[1].strip()
                    if len(body) is 4 and body[2] == 'READY':
                        player_jid = message['from'].bare
                        pygame.event.post(Event(NETWORK, msg='player_joined', game_name=room, jid=player_jid, color_id=int(body[3])))
                    elif room in self.rooms:
                        room_id = self.room_ids[room]
                        self.rooms[room].append((message['nick'], room_id))
                        message.reply("JOIN: " + room + ": SUCCESS: " + str(room_id)).send()
                        self.room_ids[room] = room_id + 1
                    else:
                        self._create_room(room, message['nick'])
                        message.reply("JOIN: " + room + ": SUCCESS: 0").send()
                if command == 'MOVE':
                    room = body[1].strip()
                    print 'Recieved move command from: ' + message['from'].bare
                    pygame.event.post(Event(NETWORK, msg='check_move', game_name=room, jid=message['from'].bare, move=body[2:]))
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        