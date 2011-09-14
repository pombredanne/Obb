import pygame, random
from pygame.locals import *
import vista, context, body, settings, panel

class Play(context.Context):
    def __init__(self):
        self.body = body.Body()
        self.panel = panel.Panel()
        self.target = None
        self.parttobuild = None
        self.edgepoint = None

    def think(self, dt, events, keys, mousepos, buttons):

        if vista.vrect.collidepoint(mousepos):
            edge = vista.grid.nearestedge(vista.screentoworld(mousepos))
            if self.panel.selected is not None:
                if edge != self.edgepoint:
                    appspec = self.panel.tiles[self.panel.selected]
                    self.parttobuild = self.body.canplaceapp(edge, appspec)
                    if self.parttobuild is not None:
                        canbuild = self.body.canaddpart(self.parttobuild)
                        self.parttobuild.status = "ghost" if canbuild else "badghost"
        else:
            edge = None
            self.parttobuild = None
        self.edgepoint = edge

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
                    self.target.die()
            if event.type == KEYUP and event.key == K_F1:
                vista.zoomin()
            if event.type == KEYUP and event.key == K_F2:
                vista.zoomout()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if vista.prect.collidepoint(mousepos):  # Click on panel
                    jtile = self.panel.iconp(mousepos)
                    if jtile in (None, 0, 1, 2):
                        self.panel.selecttile(jtile)
                elif vista.vrect.collidepoint(mousepos):
                    if self.parttobuild is not None and self.body.canaddpart(self.parttobuild):
                        self.body.addpart(self.parttobuild)
                        self.panel.claimtile()

        if keys[K_F5]:
            self.body.addrandompart()


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
        self.panel.think(dt)

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
        if self.panel.selected is not None:
            self.body.tracehexes()
        self.body.draw()
        if self.parttobuild is not None:
            self.parttobuild.draw()
        vista.addmask(self.body.mask)
        self.panel.draw()

