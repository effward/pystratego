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
		self.nick = nick
		self.get = get
		self.target_jid = target_jid
		self.target_node = target_node
		
		# Values to control which disco entities are reported
		self.info_types = ['', 'all', 'info', 'identities', 'features']
		self.identity_types = ['', 'all', 'info', 'identities']
		self.feature_types = ['', 'all', 'info', 'features']
		self.items_types = ['', 'all', 'items']
		
		# Event handlers
		self.add_event_handler("session_start", self.session_start)
		self.add_event_handler("groupchat_message", self.muc_message)
		self.add_event_handler("muc::%s::got_online" % self.room, self.muc_online)
		self.add_event_handler("message", self.message)
		self.add_event_handler("send_move", self.send_move)
		self.add_event_handler("join_room", self.join_room)
		self.add_event_handler("get_rooms", self.get_rooms)
		
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
		#self.send_message(mto=
		print 'Sending move!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
			
		#logging.debug('sending message')
		#self.send_message(mto='Admin@localhost', mbody='testing 123')
		
	def join_room(self, room_data):
		self.room = room_data
		self['xep_0045'].joinMUC(self.room, self.nick, wait=True)
		players = self['xep_0030'].get_items(jid=self.room, node=self.target_node, block=True)
		for player in players['disco_items']['items']:
			name = player[0].split('@')[0]
			print (' - %s' % name)
		if players:
			pygame.event.post(Event(NETWORK, msg='joined_room', room=self.room, count=len(players)))
		else:
			print 'Failed to connect'
			#self.disconnect()
			
	def message(self, msg):
		if msg['type'] in ('chat', 'normal'):
			msg.reply("Thanks for sending\n% (body) s" % msg).send()
			
	def muc_message(self, msg):
		if msg['mucnick'] != self.nick and self.nick in msg['body']:
			print '********' + msg['from'].bare + '**************'
			self.send_message(mto=msg['from'].bare, mbody="I heard that, %s." % msg['mucnick'], mtype='groupchat')
							  
	def muc_online(self, presence):
		if presence['muc']['nick'] != self.nick:
			print '********' + presence['from'].bare + '**************'
			self.send_message(mto=presence['from'].bare, mbody="Hello, %s %s" % (presence['muc']['role'], presence['muc']['nick']), mtype='groupchat')
			
		
		