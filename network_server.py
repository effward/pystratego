import logging, sys

from sleekxmpp.componentxmpp import ComponentXMPP

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

class EchoComponent (ComponentXMPP):
	def __init__(self, jid, secret, server, port):
		ComponentXMPP.__init__(self, jid, secret, server, port)
		
		logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
						
		
		self.add_event_handler("message", self.message)
	
	def message(self, msg):
		print 'test'
		msg.reply("Thanks for sending\n% (body)s" % msg).send()