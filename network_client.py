import ssl, logging, sys, threading, pygame
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from constants import *
from pygame.locals import *
from pygame.event import Event
from os import remove

# Sets correct default encoding depending on version of python
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

class Client(ClientXMPP, threading.Thread):
	def __init__(self, jid, password, lobby, nick, target_jid, target_node='', get=''):
		ClientXMPP.__init__(self, jid, password, sasl_mech='ANONYMOUS')
		threading.Thread.__init__(self)
		
		logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
						
		self.register_plugin('xep_0030') # Service Discovery
		self.register_plugin('old_0004')
		self.register_plugin('xep_0045') # Multi-User Chat
		self.register_plugin('xep_0199') # XMPP Ping
						
		self.lobby = lobby
		self.room = None
		self.room_nick = None
		self.nick = nick
		self.get = get
		self.target_jid = target_jid
		self.target_node = target_node
		self.players = 0
		
		# Values to control which disco entities are reported
		self.info_types = ['', 'all', 'info', 'identities', 'features']
		self.identity_types = ['', 'all', 'info', 'identities']
		self.feature_types = ['', 'all', 'info', 'features']
		self.items_types = ['', 'all', 'items']
		
		# Event handlers
		self.add_event_handler("session_start", self.session_start)
		self.add_event_handler("groupchat_message", self.muc_message)
		self.add_event_handler("message", self.message)
		self.add_event_handler("send_move", self.send_move)
		self.add_event_handler("join_room", self.join_room)
		self.add_event_handler("get_rooms", self.get_rooms)
		self.add_event_handler("create_room", self.create_room)
		
		# For use with OpenFire server
		self.ssl_version = ssl.PROTOCOL_SSLv3
		
		self.start()
		
		
	def run(self):
		if self.connect():
			self.process(block=True)
			print("done")
		else:
			print("Unable to Connect.")
		
	def session_start(self, event):
		#logging.debug('sending presence')
		self.get_roster()
		self.send_presence()
		
		# Join the lobby
		self['xep_0045'].joinMUC(self.lobby, self.nick, password='pystratego', wait=True)
		
		# Create a new room and join it
		#self['xep_0045'].joinMUC(self.room, self.nick, password='hello123', wait=True)
		#self['xep_0045'].configureRoom(self.room)
		
		if self.get in self.info_types:
			info = self['xep_0030'].get_info(jid=self.target_jid, node=self.target_node, block=True)
		if self.get in self.items_types:
			items = self['xep_0030'].get_items(jid=self.target_jid, node=self.target_node, block=True)
		else:
			logging.error("Invalid disco request type.")
			self.disconnect()
			return
		
		header = 'XMPP Service Discovery: %s' % self.target_jid
		print(header)
		print('-' * len(header))
		if self.target_node != '':
			print('Node: %s' % self.target_node)
			print('-' * len(header))
		
		if self.get in self.identity_types:
			print('Identities:')
			for identity in info['disco_info']['identities']:
				print('  - %s' % str(identity))

		if self.get in self.feature_types:
			print('Features:')
			for feature in info['disco_info']['features']:
				print('  - %s' % feature)

		if self.get in self.items_types:
			print('Items:')
			for item in items['disco_items']['items']:
				print('  - %s' % str(item))
				
		pygame.event.post(Event(NETWORK, msg='connected'))
		
	def create_room(self, room_name):
		"""self.room = room_name
		self.players = 0
		self['xep_0045'].joinMUC(self.room, self.nick, wait=True)
		self['xep_0045'].configureRoom(room)
		self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)
		python.event.post(Event(NETWORK, msg='joined_room', room=self.room, count=self.players))
		self.players += 1"""
		self.send_message(mto=SERVER_JID_PATTERN % room_name, mbody=('CREATE: ' + room_name), mtype='normal')
				
	def get_rooms(self, event):
		#self.update_roster('stratego.andrew-win7')
		rooms = self['xep_0030'].get_items(jid=self.target_jid, node=self.target_node, block=True)
		print 'Rooms:'
		FILE_LOCK.acquire()
		remove(ROOMS_FILE)
		f = open(ROOMS_FILE, 'w')
		for room in rooms['disco_items']['items']:
			name = room[0].split('@')[0]
			print (' - %s' % name)
			f.write(name)
			f.write('\n')
		f.close()
		FILE_LOCK.release()
			
		pygame.event.post(Event(NETWORK, msg='got_rooms'))
		
				
	def send_move(self, move_data):
		turn, piece, x, y = move_data
		body = 'MOVE:' + self.room_nick+ ':' + str(turn) + ':' + piece.color + ':' + piece.type + ':' + str(piece.x) + ':' + str(piece.y) + ':' + str(x) + ':' + str(y)
		self.send_message(mto=SERVER_JID_PATTERN % self.room_nick, mbody=body, mtype='normal')
			
		#logging.debug('sending message')
		#self.send_message(mto='Admin@localhost', mbody='testing 123')
		
	def join_room(self, room_name):
		self.room_nick = room_name
		self.room = ROOM_JID_PATTERN % room_name
		self.send_message(mto=SERVER_JID_PATTERN % room_name, mbody=('JOIN: ' + room_name), mtype='normal')
		self['xep_0045'].joinMUC(self.room, self.nick, wait=True)
			
	def message(self, msg):
		if msg['type'] in ('chat', 'normal'):
			body = msg['body'].split(':')
			if len(body) > 1:
				command = body[0].strip()
				if command == 'CREATE' and len(body) is 3:
					room = body[1].strip()
					result = body[2].strip()
					if result == 'SUCCESS':
						self.room_nick = room
						self.room = ROOM_JID_PATTERN % room
						self['xep_0045'].joinMUC(self.room, self.nick, wait=True)
						pygame.event.post(Event(NETWORK, msg='joined_room', room=self.room, count=0))
					else:
						self.room = None
						self.room_nick = None
						pygame.event.post(Event(NETWORK, msg='failure', details='Failed to create room'))
				if command == 'JOIN' and len(body) is 4:
					room = body[1].strip()
					result = body[2].strip()
					me = body[3].strip()
					if result == 'SUCCESS':
						pygame.event.post(Event(NETWORK, msg='joined_room', room=self.room, count=me))
							
			
	def muc_message(self, msg):
		print 'Recieved message from ' + msg['mucnick'] + ':' + msg['from'].bare
		print msg['body']
		if msg['mucnick'] != self.nick and self.nick in msg['body']:
			print '********' + msg['from'].bare + '**************'
			self.send_message(mto=msg['from'].bare, mbody="I heard that, %s." % msg['mucnick'], mtype='groupchat')
		if msg['mucnick'] == 'Admin':
			body = msg['body'].split(':')
			if len(body) > 1:
				command = body[0].strip()
				if command == 'MOVE' and len(body) is 5:
					pygame.event.post(Event(NETWORK, msg='placement_received', room=self.room, turn=body[1], color=body[2], x=body[3], y=body[4]))
				if command == 'MOVE' and len(body) is 7:
					pygame.event.post(Event(NETWORK, msg='move_received', room=self.room, turn=body[1], color=body[2], x1=body[3], y1=body[4], x2=body[5], y2=body[6]))
							  
	def muc_online(self, presence):
		if presence['muc']['nick'] != self.nick:
			self.send_message(mto=presence['from'].bare, mbody=("PLAYER: " + presence['muc']['nick'] + ":" + str(self.players)), mtype='groupchat')
			
		
		