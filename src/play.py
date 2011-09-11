import pygame, random
from pygame.locals import *
import vista, context, body, settings

class Play(context.Context):
    def __init__(self):
        self.body = body.Body()

    def think(self, dt, events, keys, mousepos, buttons):
        self.ton = vista.grid.tnearest(mousepos)
        if any(event.type == KEYDOWN for event in events):
            self.body.addrandompart()

    def draw(self):
        vista.clear()
#        for x in range(-6, 6):
#            for y in range(-6, 6):
#                vista.grid.drawhex((x,y))
        vista.grid.drawhex(self.ton, (255, 255, 255))
        self.body.draw()

