import logging, sys, threading

from sleekxmpp.componentxmpp import ComponentXMPP
from constants import *

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
		
		# Create a new room and join it
		#self['xep_0045'].joinMUC(self.room, self.nick, password='hello123', wait=True)
		#self['xep_0045'].configureRoom(self.room)
		"""
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
				"""
				
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
	
	def message(self, msg):
		if msg['type'] in ('chat', 'normal'):
			body = msg['body'].split(':')
			if len(body) > 1:
				command = body[0].strip()
				if command == 'CREATE':
					room = body[1].strip()
					self._create_room(room, msg['nick'])
					msg.reply("CREATE: " + room + ": SUCCESS").send()
				if command == 'JOIN':
					room = body[1].strip()
					if room in self.rooms:
						room_id = self.room_ids[room]
						self.rooms[room].append((msg['nick'], room_id))
						msg.reply("JOIN: " + room + ": SUCCESS: " + str(room_id)).send()
						self.room_ids[room] = room_id + 1
					else:
						self._create_room(room, msg['nick'])
						msg.reply("JOIN: " + room + ": SUCCESS: 0").send()
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						
						