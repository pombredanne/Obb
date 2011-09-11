import pygame, random
from pygame.locals import *
import vista, context, body, settings

class Play(context.Context):
    def __init__(self):
        self.body = body.Body()
        self.drawmask()

    def drawmask(self):        
        px, py = self.body.core.screenpos()
        ps = [((px/10, py/10), 20)]
        for part in self.body.parts:
            if isinstance(part, body.Organ):
                px, py = part.screenpos()
                ps.append(((px/10, py/10), 20))
        self.mask = vista.Mask((settings.sx/10, settings.sy/10), ps)
        self.mask = pygame.transform.smoothscale(self.mask.surf, settings.size)

    def think(self, dt, events, keys, mousepos, buttons):
        self.ton = vista.grid.tnearest(mousepos)
        if any(event.type == KEYDOWN for event in events):
            self.body.addrandompart()
            self.drawmask()

    def draw(self):
        vista.clear()
#        for x in range(-6, 6):
#            for y in range(-6, 6):
#                vista.grid.drawhex((x,y))
        vista.grid.drawhex(self.ton, (255, 255, 255))
        self.body.draw()
        vista.screen.blit(self.mask, (0,0))

