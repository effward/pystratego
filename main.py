import pygame, sys, random, os
import helper, board, player
from pygame.locals import *
from events import *
from constants import *
from weakref import WeakKeyDictionary

class EventManager:
	def __init__(self):
		self.listeners = WeakKeyDictionary()
		self.eventQueue = []
		
	def register_listener(self, listener):
		self.listeners[listener] = 1
		
	def unregister_listener(self, listener):
		if listener in self.listeners.keys():
			del self.listeners[listener]
			
	def post(self, event):
		from copy import copy
		if not isinstance(event, TickEvent):
			self.eventQueue.append(event)
		else:
			events = copy(self.eventQueue)
			self.eventQueue = []
			while len(events) > 0:
				ev = events.pop(0)
				self.Debug(ev)
				
				for listener in self.listeners.keys():
					listener.notify(ev)
			
			for listener in self.listeners.keys():
				listener.notify(event)
				
class CPUSpinnerController:
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.register_listener(self)
		self.running = 1
		
	def run(self):
		if not self.running:
			raise Exception('dead spinner')
		while self.running:
			self.evManager.post(TickEvent())
			
	def notify(self, event):
		if isinstance(event, QuitEvent):
			self.running = 0
			
class PygameMasterController:
	def __init__(self, evManager):
		self.evManager = evManager
		self.evManager.register_listener(self)
		
		# subcontrollers is an ordered list, the first controller in the list is the first to be offered an event
		self.subcontrollers = []
		
		self.guiClasses = {'menu': [SimpleGUIController],
									'options': [SimpleGUIController],
									'main': [MainGUIController, MainBarScreenController],
									}
		self.dialogClasses = {'msgDialog': BlockingDialogController,
										}
		self.switch_controller('menu')
		
	def switch_controller(self, key):
		if not self.guiClasses.has_key(key):
			raise NotImplementedError
			
		self.subcontrollers = []
		for contClass in self.guiClasses[key]:
			newController = contClass(self.evManager)
			self.subcontrollers.append(newController)
			
	def dialog_add(self, key):
		if not self.dialogClasses.has_key( key ):
			raise NotImplementedError

		contClass = self.dialogClasses[key]
		newController = contClass(self.evManager)

		self.subcontrollers.insert(0, newController)
		
	def dialog_remove(self, key):
		if not self.dialogClasses.has_key( key ):
			raise NotImplementedError

		contClass = self.dialogClasses[key]

		if self.subcontrollers[0].__class__ is not contClass:
			print self.subcontrollers
			raise Exception('removing dialog controller not there')

		self.subcontrollers.pop(0)
		
	def notify(self, incomingEvent):
		if isinstance( incomingEvent, TickEvent ):
			#Handle Input Events
			for event in pygame.event.get():
				ev = None
				if event.type == QUIT:
					ev = QuitEvent()
					self.evManager.post( ev )

				elif event.type == KEYDOWN \
				  or event.type == MOUSEBUTTONUP \
				  or event.type == MOUSEMOTION:
					for cont in self.subcontrollers:
						if cont.WantsEvent( event ):
							cont.HandlePyGameEvent(event)
							break

		elif isinstance( incomingEvent, GUIChangeScreenRequest ):
			self.switch_controller( incomingEvent.key )

		elif isinstance( incomingEvent, GUIDialogAddRequest ):
			self.dialog_add( incomingEvent.key )

		elif isinstance( incomingEvent, GUIDialogRemoveRequest ):
			self.dialog_remove( incomingEvent.key )
			
class PygameMasterView(EventManager):
	def __init__(self, evManager):
		EventManager.__init__(self)
		self.normalListeners = self.listeners
		self.dialogListeners = WeakKeyDictionary()
		
		self.evManager = evManager
		self.evManager.register_listener(self)
		
		pygame.init()
		self.window = pygame.display.set_mode(SCREEN_SIZE)
		pygame.display.set_caption('pyStratego')
		self.background, self.background_rect = helper.load_image("bg.bmp")
		self.window.blit(self.background,(0,0))
		pygame.display.flip()
		
		self.dialog = None
		
		self.subviews = []
		self.spriteGroup = LayeredSpriteGroup()
		
		self.guiClasses = { 'menu': [MenuGUIView],
									'options': [OptionsGUIView],
									'main': [MainBarScreen, MainGUIView],
								  }
		self.dialogClasses = { 'msgDialog': BlockingDialogView,
										}
										
		self.switch_view('menu')
		
	def debug(self, ev):
		return
		if not isinstance(ev, GUIMouseMoveEvent):
			print '		Message: ', ev.name
			
	def post(self, event):
		self.evManager.post(event)
		
	def switch_view(self, key):
		if self.dialog:
			raise Excpetion('cannot switch view while dialog up')
			
		if not self.guiClasses.has_key(key):
			raise NotImplementedError('master view doesnt have key')
			
		for view in self.subviews:
			view.kill()
		self.subviews = []
		
		self.spriteGroup.empty()
		
		rect = pygame.Rect((0,0), self.window.get_size())
		
		for viewClass in self.guiClasses[key]:
			if hasattr(viewClass, 'clipRect'):
				rect = viewClass.clipRect
			view = viewClass(self, self.spriteGroup, rect)
			bgBlit = view.GetBackgroundBlit()
			self.background.blit(bgBlit[0], bgBlit[1])
			self.subviews.append(view)
			
			self.window.blit(self.background, (0,0))
			pygame.display.flip()
			
	def dialog_add(self, key, msg="error"):
		if self.dialog:
			raise Exception('only one dialog at a time')

		if not self.dialogClasses.has_key( key ):
			raise NotImplementedError('master view doesnt have key')

		#the normal listeners will not be sent any events.  instead,
		#we will just send events to the listeners associated with the
		#new dialog.
		self.listeners = self.dialogListeners


		rect = pygame.Rect( (0,0), self.window.get_size() )

		dialogClass = self.dialogClasses[key]
		if hasattr( dialogClass, 'clipRect' ):
			rect = dialogClass.clipRect
		self.dialog = dialogClass(self, self.spriteGroup, rect )
		if hasattr( self.dialog, 'SetMsg' ):
			self.dialog.SetMsg( msg )

		self.subviews.append( self.dialog )
		
	def dialog_remove(self, key):
		if not self.dialogClasses.has_key( key ):
			raise NotImplementedError

		if self.dialog.__class__ is not self.dialogClasses[key]:
			raise Exception( 'that dialog is not open' )

		#after the dialog is removed, the normal listeners should start
		#receiving events again.
		self.listeners = self.normalListeners

		self.dialog.kill()
		self.subviews.remove( self.dialog )
		self.dialog = None

	def handle_tick(self):
		self.spriteGroup.clear(self.window, self.background)
		self.spriteGroup.update()
		dirtyRects = self.spriteGroup.draw(self.window)
		pygame.display.update(dirtyRects)
		
	def notify(self, event):
		if isinstance( event, GUIChangeScreenRequest ):
			self.switch_view( event.key )

		elif isinstance( event, TickEvent ):
			self.handle_tick()

		elif isinstance( event, GUIDialogAddRequest ):
			self.dialog_add( event.key, event.msg )

		elif isinstance( event, ExceptionEvent):
			ev = GUIDialogAddRequest( 'msgDialog', event.msg )
			self.evManager.post( ev )

		elif isinstance( event, GUIDialogRemoveRequest ):
			self.dialog_remove( event.key )

		#at the end, handle the event like an EventManager should
		EventManager.post( self, event )
		
def main():
	evManager = EventManager()
	
	spinner = CPUSpinnerController(evManager)
	pygameView = PygameMasterView(evManager)
	pygameCont = PygameMasterController(evManager)
	game = Game(evManager)
	
	while 1:
		try:
			spinner.run()
		except NotImplementedError, msg:
			text = "Not Implemented: "+ str(msg)
			ev = ExceptionEvent( text )
			evManager.post( ev )
		else:
			break;
	"""
	b = board.Board()
	player1 = player.Player('red')
	
	running = 1
	# 0 = pre-game, 1 = game, 2 = post-game
	mode = 0
	
	while running:
		for event in pygame.event.get():
			if event.type == QUIT: sys.exit()
			# Process Keyboard input
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = 0
			# Process Mouse input
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					pass
					
		b.clear(screen, background)
		b.update()
		b.draw(screen)
		
		player1.pieces.clear(screen, background)
		player1.pieces.update()
		player1.pieces.draw(screen)
					
		pygame.display.flip()
		"""
		
if __name__ == '__main__': main()