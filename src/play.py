import pygame, random
from pygame.locals import *
import vista, context, body, settings, panel, status, noise, twinkler, enemy, graphics

class Play(context.Context):
    def __init__(self):
        self.body = body.Body()
        self.panel = panel.Panel()
        self.status = status.Status(self.body)
        self.target = None
        self.parttobuild = None
        self.edgepoint = None
        self.iconclicked = None
        self.twinklers = []
        self.shots = []
        self.paused = False

    def think(self, dt, events, keys, mousepos, buttons):

        if self.paused:
            if any(e.type == KEYDOWN or e.type == MOUSEBUTTONDOWN for e in events):
                self.resume()
            return


        if vista.vrect.collidepoint(mousepos):
            edge = vista.grid.nearestedge(vista.screentoworld(mousepos))
            if edge != self.edgepoint:
                if self.panel.selected is not None:
                    appspec = self.panel.tiles[self.panel.selected]
                    self.parttobuild = self.body.canplaceapp(edge, appspec)
                elif self.status.selected is not None:
                    otype = self.status.selected
                    self.parttobuild = self.body.canplaceorgan(edge, otype)
                if self.parttobuild is not None:
                    worldpos = vista.HexGrid.edgeworld(*edge)
                    visible = self.body.mask.isvisible(worldpos)
                    self.canbuild = self.body.canaddpart(self.parttobuild) and visible
                    self.parttobuild.status = "ghost" if self.canbuild else "badghost"
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
                self.handleleftclick(mousepos)

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

        vista.think(dt, mousepos, keys)

        self.body.think(dt)
        self.panel.think(dt)
        self.status.think(dt, mousepos)
        self.twinklers += twinkler.newtwinklers(self.body.mask, dt)
        for t in self.twinklers:
            t.think(dt)
        self.twinklers = [t for t in self.twinklers if t.alive()]
        self.body.claimtwinklers(self.twinklers)
        self.body.attackenemies(self.shots)
        if random.random() < dt:
            self.shots += enemy.newshots(self.body)
        for s in self.shots: s.think(dt)
        self.shots = [s for s in self.shots if s.alive()]
        self.status.mutagenmeter.amount += self.body.checkmutagen()

    def pause(self):
        self.paused = True
        self.pscreen = graphics.ghostify(vista._screen)
        noise.pause()

    def resume(self):
        self.paused = False
        self.pscreen = None
        noise.resume()

    def handleleftclick(self, mousepos):
        bicon = self.status.iconpoint(mousepos)  # Any build icons pointed to
        vicon = vista.iconhit(mousepos)  # Any vista icons pointed to
        if self.panel.trashp(mousepos):  # Click on trash icon
            if self.panel.selected is not None:
                self.panel.claimtile()
                noise.play("trash")
            self.status.select()
            self.parttobuild = None
        elif vista.prect.collidepoint(mousepos):  # Click on panel
            jtile = self.panel.iconp(mousepos)
            if jtile in (None, 0, 1, 2):
                self.panel.selecttile(jtile)
            self.status.select()
        elif vicon == "zoomin":
            vista.zoomin()
        elif vicon == "zoomout":
            vista.zoomout()
        elif vicon == "pause":
            self.pause()
        elif vicon == "music":
            noise.nexttrack()
        elif bicon is not None:
            self.status.select(bicon.name)
            self.panel.selecttile()
        elif vista.vrect.collidepoint(mousepos):
            if self.parttobuild is not None and self.canbuild and self.body.canaddpart(self.parttobuild):
                self.body.addpart(self.parttobuild)
                if self.panel.selected is not None:
                    self.panel.claimtile()
                if self.status.selected is not None:
                    self.status.build()
                self.parttobuild = None

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
        if self.paused:
            vista._screen.blit(self.pscreen, (0,0))
            pygame.display.flip()
            return
        vista.clear()
        if self.panel.selected is not None or self.status.selected is not None:
            self.body.tracehexes()
        self.body.draw()
        if self.parttobuild is not None:
            self.parttobuild.draw()
        for t in self.twinklers: t.draw()
        for s in self.shots: s.draw()
        vista.addmask(self.body.mask)
        self.panel.draw()
        self.status.draw()
        vista.flip()


