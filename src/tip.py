import pygame
from pygame.locals import *
import font, graphics, settings

currenttip = ""
def settip(newtip = ""):
	global currenttip
	currenttip = newtip


ticker = 0
def think(dt):
	global surf, rect, ticker, bheight
	import vista
	if not settings.showtips: return
	if not currenttip:
		surf = None
		ticker = max(ticker - dt, 0)
	else:
		surf = font.blocktext(currenttip, size = settings.layout.tipsize)
		bheight = surf.get_height()
		ticker = min(ticker + dt, 0.25)


def draw():
	"""Should be called after the main blit, even after the overlays"""
	import vista
	currenttip = ""
	if not settings.showtips:
		return
	if ticker:
		bubble = graphics.thoughtbubble(bheight, f = ticker*4)
		bubblerect = bubble.get_rect(midtop = vista.vrect.midtop)
		vista._screen.blit(bubble, bubblerect)
	if surf and ticker == 0.25:
		rect = surf.get_rect(center = bubblerect.center)
		vista._screen.blit(surf, rect)

