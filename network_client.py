import ssl, logging, sys, threading
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from constants import *

# Sets correct default encoding depending on version of python
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

class Client(ClientXMPP, threading.Thread):
	def __init__(self, jid, password, room, nick, target_jid, target_node='', get=''):
		ClientXMPP.__init__(self, jid, password, sasl_mech='ANONYMOUS')
		threading.Thread.__init__(self)
		
		logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
						
		self.register_plugin('xep_0030') # Service Discovery
		self.register_plugin('old_0004')
		self.register_plugin('xep_0045') # Multi-User Chat
		self.register_plugin('xep_0199') # XMPP Ping
						
		self.room = room
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
		self['xep_0045'].joinMUC('lobby@stratego.andrew-win7', self.nick, password='pystratego', wait=True)
		
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

			
		#logging.debug('sending message')
		#self.send_message(mto='Admin@localhost', mbody='testing 123')
			
	def message(self, msg):
		if msg['type'] in ('chat', 'normal'):
			msg.reply("Thanks for sending\n% (body) s" % msg).send()
			
	def muc_message(self, msg):
		if msg['mucnick'] != self.nick and self.nick in msg['body']:
			self.send_message(mto=msg['from'].bare, mbody="I heard that, %s." % msg['mucnick'], mtype='groupchat')
							  
	def muc_online(self, presence):
		if presence['muc']['nick'] != self.nick:
			self.send_message(mto=presence['from'].bare, mbody="Hello, %s %s" % (presence['muc']['role'], presence['muc']['nick']), mtype='groupchat')
			
		
		