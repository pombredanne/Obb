# The options menu context

import pygame
from pygame.locals import *
import context, graphics, vista, settings, font

from i18n import _

class Button(object):
	def __init__(self, text, buttonset, onselect = None, onconfirm = None):
		self.text = text
		self.buttonset = buttonset
		img0 = font.blocktext(text, size = settings.layout.tipsize)
		w0, h0 = img0.get_size()
		m = settings.layout.menubuttonmargin
		self.img = vista.Surface(w0 + 2*m, h0 + 2*m)
		self.img.blit(img0, (m, m))
		self.onselect = onselect
		self.onconfirm = onconfirm
		self.rect = self.img.get_rect()
		self.selected = False
	
	
	def select(self):
		for button in self.buttonset.buttons:
			button.selected = button is self
		if self.onselect is not None:
			self.onselect()
	
	
	def confirm(self):
		if self.onconfirm is not None:
			self.onconfirm()
	
	
	def draw(self):
		img = self.img
		if self.selected:
			pygame.draw.rect(vista._screen, (255, 128, 128), self.rect, 2)
		vista._screen.blit(self.img, self.rect)


class ButtonSet(object):
	def __init__(self, texts, args, maxwidth, onconfirm = None, onselects = None):
		self.buttons = []
		self.buttonmap = {}
		for j in range(len(texts)):
			# I swear I don't know a better way to do this
			# http://fora.xkcd.com/viewtopic.php?f=11&t=4052
			f = onconfirm and (lambda z: (lambda: onconfirm(z)))(args[j])
			g = onselects and onselects[j]
			button = Button(texts[j], self, onconfirm = f, onselect = g)
			self.buttons.append(button)
			self.buttonmap[args[j] if args else texts[j]] = button
		self.rows = []
		width = 0
		for button in self.buttons:
			w = button.img.get_width()
			if not self.rows or width + w + settings.layout.menudx > maxwidth:
				self.rows.append([button])
				width = w
			else:
				self.rows[-1].append(button)
				width += w + settings.layout.menudx
		self.width = 0
		self.height = 0
		for row in self.rows:
			ws = [button.rect.width for button in row]
			hs = [button.rect.height for button in row]
			wsum = sum(ws) + settings.layout.menudx * (len(ws) - 1)
			x = settings.sx / 2 - wsum / 2
			for button in row:
				button.rect.left = x
				x = button.rect.right + settings.layout.menudx
			self.width = max(self.width, wsum)
			self.height += max(hs) # + (self.height and settings.layout.menudy)
	
	
	def sety(self, y):
		for row in self.rows:
			for button in row:
				button.rect.top = y
			y += max(button.rect.height for button in row) # + settings.layout.menudy
	
	
	def draw(self):
		for button in self.buttons:
			button.draw()


class Menu(context.Context):
	def __init__(self):
		self.background = graphics.ghostify(vista._screen.convert_alpha())
		self.cloudticker = 0
		self.active = True
		self.width = maxwidth = int(settings.sx * 0.75)
		
		rs = settings.getresolutions()
		rtexts = ["%sx%s" % res for res in rs]
		rescallback = lambda arg: settings.setresolution(*arg)
		self.resbuttons = ButtonSet(rtexts, rs, maxwidth, rescallback)
		self.resbuttons.buttonmap[settings.size].selected = True
		
		wargs = [False, True]
		wtexts = [_("window mode"), _("fullscreen mode")]
		def wcallback(arg): settings.fullscreen = arg
		self.wbuttons = ButtonSet(wtexts, wargs, maxwidth, wcallback)
		self.wbuttons.buttonmap[settings.fullscreen].selected = True
		
		args = [0.5, 1., 2.]
		texts = [_("slow"), _("normal"), _("fast")]
		def callback(arg): settings.gamespeed = arg
		speedbuttons = ButtonSet(texts, args, maxwidth, callback)
		speedbuttons.buttonmap[settings.gamespeed].selected = True
		
		args = [False, True]
		texts = [_("sound on"), _("sound off")]
		def callback(arg): settings.silent = arg
		soundbuttons = ButtonSet(texts, args, maxwidth, callback)
		soundbuttons.buttonmap[settings.silent].selected = True
		
		args = [True, False]
		texts = [_("star field on"), _("star field off")]
		def callback(arg): settings.showstars = arg
		starbuttons = ButtonSet(texts, args, maxwidth, callback)
		starbuttons.buttonmap[settings.showstars].selected = True
		
		texts = [_("back to game"), _("quit game")]
		callbacks = [self.backtogame, self.quitgame]
		donebuttons = ButtonSet(texts, None, maxwidth, onselects = callbacks)
		
		self.buttonsets = [soundbuttons, self.resbuttons, self.wbuttons, speedbuttons, starbuttons, donebuttons]
		hs = [buttonset.height for buttonset in self.buttonsets]
		self.height = sum(hs) + settings.layout.menudy * (len(hs) - 1)
		y = settings.sy / 2 - self.height / 2
		for buttonset in self.buttonsets:
			buttonset.sety(y)
			y += buttonset.height + settings.layout.menudy
	
	
	def backtogame(self):
		self.active = False
	
	
	def quitgame(self):
		context.pop(2)
		context.push(self)
		self.active = False        
	
	
	def think(self, dt, events, keys, mousepos, buttons):
		if self.active:
			self.cloudticker = min(self.cloudticker + dt, 0.25)
		else:
			self.cloudticker = max(self.cloudticker - dt, 0)
			if not self.cloudticker:
				self.finish()
		
		for event in events:
			if event.type == MOUSEBUTTONDOWN and event.button == 1:
				if self.active:
					for buttonset in self.buttonsets:
						for button in buttonset.buttons:
							if button.rect.collidepoint(mousepos):
								button.select()
			if event.type == MOUSEBUTTONDOWN and event.button == 3:
				self.backtogame()
	
	
	def finish(self):
		newres = not self.resbuttons.buttonmap[settings.size].selected
		newwin = not self.wbuttons.buttonmap[settings.fullscreen].selected
		for buttonset in self.buttonsets:
			for button in buttonset.buttons:
				if button.selected:
					button.confirm()
		context.pop()
		settings.save()
		settings.load()
		if newres or newwin:
			vista.init()
	
	
	def draw(self):
		vista._screen.blit(self.background, (0,0))
		bubble = graphics.thoughtbubble(self.height, self.width, f = self.cloudticker*4)
		bubblerect = bubble.get_rect(center = (settings.sx/2, settings.sy/2))
		vista._screen.blit(bubble, bubblerect)
		if self.cloudticker == 0.25:
			for buttonset in self.buttonsets:
				buttonset.draw()
		pygame.display.flip()