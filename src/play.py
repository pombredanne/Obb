import pygame, random
from pygame.locals import *
import vista, context, body, settings, panel, status, noise, twinkler, enemy, graphics

class Play(context.Context):
    def __init__(self):
        self.body = body.Body()
        self.panel = panel.Panel(self.body)
        self.status = status.Status(self.body)
        self.edgepoint = None
        self.twinklers = []
        self.shots = []
        self.paused = False
        self.target = None
        self.clearselections()

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
            if event.type == MOUSEBUTTONDOWN and event.button == 4 and settings.zoomonscroll:
                vista.zoomin()
            if event.type == MOUSEBUTTONDOWN and event.button == 5 and settings.zoomonscroll:
                vista.zoomout()

        if keys[K_F5]:
            self.body.addrandompart()

        if keys[K_x] or self.cutmode:
            newtarget = self.pointchildbyedge(mousepos)
            if newtarget != self.target:
                if self.target is not None:
                    self.target.setbranchstatus()
                self.target = newtarget
                if self.target is not None:
                    self.target.setbranchstatus("target")
        elif self.healmode:
            newtarget = self.body.nearestorgan(vista.screentoworld(mousepos))
            self.target = newtarget
            #if newtarget != self.target:
            #    if self.target is not None:
            #        self.target.setbranchstatus()
            #    self.target = newtarget
            #    if self.target is not None:
            #        self.target.setstatus("toheal")
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
        self.status.setheights(self.body.maxmutagen, self.body.maxplaster)
        self.status.mutagenmeter.amount += self.body.checkmutagen()
        self.status.healmeter.amount += self.body.checkplaster()

    def pause(self):
        self.paused = True
        self.pscreen = graphics.ghostify(vista._screen)
        noise.pause()

    def resume(self):
        self.paused = False
        self.pscreen = None
        noise.resume()

    def clearselections(self, clearpanel = True, clearstatus = True, clearheal = True, clearcut = True):
        if self.target is not None:
            self.target.setbranchstatus()
        self.target = None
        self.parttobuild = None
        self.iconclicked = None
        if clearpanel:
            self.panel.selecttile()
        if clearstatus:
            self.status.select()
        if clearheal:
            self.healmode = False
        if clearcut:
            self.cutmode = False

    def handleleftclick(self, mousepos):
        bicon = self.status.iconpoint(mousepos)  # Any build icons pointed to
        vicon = vista.iconhit(mousepos)  # Any vista icons pointed to
        if vicon == "trash":
            if self.panel.selected is not None:
                self.panel.claimtile()
                noise.play("trash")
            self.clearselections()
        elif vicon == "zoomin":
            vista.zoomin()
        elif vicon == "zoomout":
            vista.zoomout()
        elif vicon == "pause":
            self.pause()
        elif vicon == "music":
            noise.nexttrack()
        elif vicon == "heal":
            if self.healmode:
                self.clearselections()
            else:
                self.clearselections()
                if vista.icons["heal"].active:
                    self.healmode = True
        elif vicon == "cut":
            if self.cutmode:
                self.clearselections()
            else:
                self.clearselections()
                if vista.icons["cut"].active:
                    self.cutmode = True
        elif vista.prect.collidepoint(mousepos):  # Click on panel
            self.clearselections(clearpanel = False)
            jtile = self.panel.iconp(mousepos)
            if jtile in (None, 0, 1, 2, 3, 4, 5):
                self.panel.selecttile(jtile)
        elif bicon is not None:
            self.clearselections(clearstatus = False)
            self.status.select(bicon.name)
        elif vista.vrect.collidepoint(mousepos):
            if self.cutmode and self.target is not None:
                self.target.die()
            elif self.healmode and self.target is not None:
                dhp = self.target.heal()
                self.status.usehp(dhp)
            elif self.parttobuild is not None and self.canbuild and self.body.canaddpart(self.parttobuild):
                if self.panel.selected is not None:
                    self.panel.claimtile()
                if self.status.selected is not None:
                    self.status.build()
                self.body.addpart(self.parttobuild)
                self.clearselections()

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


