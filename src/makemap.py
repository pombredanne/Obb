import pygame, random
import context, vista, graphics, settings, game, font

from i18n import _

class MakeMap(context.Context):
	def __init__(self):
		self.background = graphics.ghostify(vista._screen.convert_alpha())
		self.cloudticker = 0
		self.active = True
		text = _("Saving map to %s....") % settings.mapfile
		self.textimg = font.blocktext(text, size = settings.layout.tipsize)
		self.drawn = False
		self.savestate()
	
	
	def savestate(self):
		"""Save the relevant pieces of the game state so they can be restored when we're done"""
		grect = vista.wx0, vista.wy0, vista.wx1, vista.wy1
		vrect = settings.vx0, settings.vy0, settings.vx, settings.vy
		gxy = vista.gx0, vista.gy0
		self.state = vista.zoom, grect, vrect, vista.vrect, vista.screen, vista.stars, gxy
	
	
	def restorestate(self):
		vista.zoom, grect, vrect, vista.vrect, vista.screen, vista.stars, gxy = self.state
		vista.setgrect(grect)
		settings.vx0, settings.vy0, settings.vx, settings.vy = vrect
		vista.gx0, vista.gy0 = gxy
	
	
	def makeit(self):
		vista.zoom = settings.mapzoom
		game.state.body.remakemask()
		vista.setgrect(game.state.body.mask.bounds())
		
		x0, y0 = vista.worldtoscreen((vista.wx0, vista.wy1))
		x1, y1 = vista.worldtoscreen((0, 0))
		x2, y2 = vista.worldtoscreen((vista.wx1, vista.wy0))
		
		settings.vx0, settings.vy0 = 0, 0
		settings.vx, settings.vy = x, y = x2 - x0, y2 - y0
		
		vista.vrect = pygame.Rect(0, 0, x, y)
		vista.screen = vista.Surface((x, y), alpha = False)
		vista.stars = [(random.randint(64, 255), random.randint(-10000, 10000), random.randint(-10000, 10000))
			for _ in range(x * y / 2000)]
		vista.stars.sort()
		
		vista.gx0 = x1-x0
		vista.gy0 = y1-y0
		
		vista.clear()
		game.state.draw()
		pygame.image.save(vista.screen, settings.mapfile)
	
	
	def think(self, dt, events, keys, mousepos, buttons):
		if self.active:
			self.cloudticker = min(self.cloudticker + dt, 0.25)
		else:
			self.cloudticker = max(self.cloudticker - dt, 0)
			if not self.cloudticker:
				self.restorestate()
				context.pop()
		
		if self.drawn and self.active:
			self.makeit()
			self.active = False
	
	
	def draw(self):
		vista._screen.blit(self.background, (0,0))
		width, height = self.textimg.get_size()
		bubble = graphics.thoughtbubble(height, width, f = self.cloudticker*4)
		bubblerect = bubble.get_rect(center = (settings.sx/2, settings.sy/2))
		vista._screen.blit(bubble, bubblerect)
		if self.cloudticker == 0.25:
			rect = self.textimg.get_rect(center = vista._screen.get_rect().center)
			vista._screen.blit(self.textimg, rect)
			self.drawn = True
		pygame.display.flip()