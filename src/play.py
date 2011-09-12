import pygame, random
from pygame.locals import *
import vista, context, body, settings

class Play(context.Context):
    def __init__(self):
        self.body = body.Body()

    def think(self, dt, events, keys, mousepos, buttons):
        for event in events:
            if event.type == KEYDOWN and event.key == K_SPACE:
                self.body.addrandompart()
            if event.type == KEYDOWN and event.key == K_v:
                wpos = vista.screentoworld(mousepos)
                print "Visibility:", self.body.mask.visibility(wpos)
            if event.type == KEYDOWN and event.key == K_x:
                child = self.pointchildbyedge(mousepos)
                print "Target:", child
                if child is not None:
                    self.body.removebranch(child)
                
                
        self.body.think(dt)

    def pointchildbyedge(self, screenpos):
        edge = vista.grid.nearestedge(vista.screentoworld(screenpos))
        edge = vista.grid.normedge(*edge)
        if edge not in self.body.takenedges:
            return None
        parent = self.body.takenedges[edge]
        if edge not in parent.buds:
            edge = vista.grid.opposite(*edge)
        return parent.buds[edge]
        

    def draw(self):
        vista.clear()
#        for x in range(-6, 6):
#            for y in range(-6, 6):
#                vista.grid.drawhex((x,y))
#        vista.grid.drawhex(self.ton, (255, 255, 255))
        self.body.draw()
        vista.addmask(self.body.mask)

