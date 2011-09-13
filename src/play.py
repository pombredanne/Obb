import pygame, random
from pygame.locals import *
import vista, context, body, settings

class Play(context.Context):
    def __init__(self):
        self.body = body.Body()
        self.target = None

    def think(self, dt, events, keys, mousepos, buttons):
        for event in events:
            if event.type == KEYDOWN and event.key == K_SPACE:
                self.body.addrandompart()
            if event.type == KEYDOWN and event.key == K_BACKSPACE:
                self.body.addrandompart(20)
            if event.type == KEYDOWN and event.key == K_v:
                wpos = vista.screentoworld(mousepos)
                print "Visibility:", self.body.mask.visibility(wpos)
            if event.type == KEYUP and event.key == K_x:
                if self.target is not None:
                    self.body.removebranch(self.target)
            if event.type == KEYUP and event.key == K_F1:
                vista.zoomin()
            if event.type == KEYUP and event.key == K_F2:
                vista.zoomout()
                


        if keys[K_x]:
            newtarget = self.pointchildbyedge(mousepos)
            if newtarget != self.target:
                if self.target is not None:
                    self.target.setbranchstatus()
                self.target = newtarget
                if self.target is not None:
                    self.target.setbranchstatus("target")
        elif self.target is not None:
            self.target.setbranchstatus()
            self.target = None

        vista.think(dt, mousepos)
                
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

