"""
Creating a SleekXMPP Plugin

This is a minimal implementation of XEP-0077 to serve
as a tutorial for creating SleekXMPP plugins.
"""

from sleekxmpp.plugins.base import base_plugin
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher.xpath import MatchXPath
from sleekxmpp.xmlstream import ElementBase, ET, JID, register_stanza_plugin
from sleekxmpp import Iq
import copy


class Registration(ElementBase):
    namespace = 'jabber:iq:register'
    name = 'query'
    plugin_attrib = 'register'
    interfaces = set(('username', 'password', 'email', 'nick', 'name', 
                      'first', 'last', 'address', 'city', 'state', 'zip', 
                      'phone', 'url', 'date', 'misc', 'text', 'key', 
                      'registered', 'remove', 'instructions'))
    sub_interfaces = interfaces

    def getRegistered(self):
        present = self.xml.find('{%s}registered' % self.namespace)
        return present is not None

    def getRemove(self):
        present = self.xml.find('{%s}remove' % self.namespace)
        return present is not None

    def setRegistered(self, registered):
        if registered:
            self.addField('registered')
        else:
            del self['registered']

    def setRemove(self, remove):
        if remove:
            self.addField('remove')
        else:
            del self['remove']

    def addField(self, name):
        itemXML = ET.Element('{%s}%s' % (self.namespace, name))
        self.xml.append(itemXML)


class UserStore(object):
    def __init__(self):
        self.users = {}

    def __getitem__(self, jid):
        return self.users.get(jid, None)

    def register(self, jid, registration):
        username = registration['username']

        def filter_usernames(user):
            return user != jid and self.users[user]['username'] == username

        conflicts = filter(filter_usernames, self.users.keys())
        if conflicts:
            return False

        self.users[jid] = registration
        return True

    def unregister(self, jid):
        del self.users[jid]

class xep_0077(base_plugin):
    """
    XEP-0077 In-Band Registration
    """

    def plugin_init(self):
        self.description = "In-Band Registration"
        self.xep = "0077"
        self.form_fields = ('username', 'password')
        self.form_instructions = ""
        self.backend = UserStore()

        self.xmpp.registerHandler(
            Callback('In-Band Registration',
                     MatchXPath('{%s}iq/{jabber:iq:register}query' % self.xmpp.default_ns),
                     self.__handleRegistration))
        register_stanza_plugin(Iq, Registration)

    def post_init(self):
        base_plugin.post_init(self)
        self.xmpp['xep_0030'].add_feature("jabber:iq:register")

    def __handleRegistration(self, iq):
        if iq['type'] == 'get':
            # Registration form requested
            userData = self.backend[iq['from'].bare]
            self.sendRegistrationForm(iq, userData)
        elif iq['type'] == 'set':
            if iq['register']['remove']:
                # Remove an account
                self.backend.unregister(iq['from'].bare)
                self.xmpp.event('unregistered_user', iq)
                iq.reply().send()
                return

            for field in self.form_fields:
                if not iq['register'][field]:
                    # Incomplete Registration
                    self._sendError(iq, '406', 'modify', 'not-acceptable',
                                    "Please fill in all fields.")
                    return

            if self.backend.register(iq['from'].bare, iq['register']):
                # Successful registration
                self.xmpp.event('registered_user', iq)
                iq.reply().setPayload(iq['register'].xml)
                iq.send()
            else:
                # Conflicting registration
                self._sendError(iq, '409', 'cancel', 'conflict',
                                "That username is already taken.")

    def setForm(self, *fields):
        self.form_fields = fields

    def setInstructions(self, instructions):
        self.form_instructions = instructions

    def sendRegistrationForm(self, iq, userData=None):
        reg = iq['register']
        if userData is None:
            userData = {}
        else:
            reg['registered'] = True

        if self.form_instructions:
            reg['instructions'] = self.form_instructions

        for field in self.form_fields:
            data = userData.get(field, '')
            if data:
                # Add field with existing data
                reg[field] = data
            else:
                # Add a blank field
                reg.addField(field)

        iq.reply().setPayload(reg.xml)
        iq.send()

    def _sendError(self, iq, code, error_type, name, text=''):
        iq.reply().setPayload(iq['register'].xml)
        iq.error()
        iq['error']['code'] = code
        iq['error']['type'] = error_type
        iq['error']['condition'] = name
        iq['error']['text'] = text
        iq.send()