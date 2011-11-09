import pygame, random
from pygame.locals import *
import vista, context, settings, noise, graphics, tip, mechanics, game, status, panels, menu

class Play(context.Context):
    def __init__(self):
        self.edgepoint = None
        self.target = None
        self.healmode = False
        self.clearselections()
        self.clickat = None

    def think(self, dt, events, keys, mousepos, buttons):
        if vista.vrect.collidepoint(mousepos):
            edge = vista.grid.nearestedge(vista.screentoworld(mousepos))
            if edge != self.edgepoint:
                if panels.selectedtile is not None:
                    appspec = status.state.tiles[panels.selectedtile]
                    self.parttobuild = game.state.body.canplaceapp(edge, appspec)
                elif panels.selectedorgan is not None:
                    otype = panels.selectedorgan
                    self.parttobuild = game.state.body.canplaceorgan(edge, otype)
                if self.parttobuild is not None:
                    worldpos = vista.HexGrid.edgeworld(*edge)
                    visible = game.state.body.mask.isvisible(worldpos)
                    self.canbuild = game.state.body.canaddpart(self.parttobuild) and visible
                    self.parttobuild.status = "ghost" if self.canbuild else "badghost"
        else:
            edge = None
            self.parttobuild = None
        self.edgepoint = edge

        for event in events:
            if event.type == KEYDOWN and event.key == K_SPACE:
                if settings.debugkeys:
                    game.state.body.addrandompart()
            if event.type == KEYDOWN and event.key == K_BACKSPACE:
                if settings.debugkeys:
                    game.state.body.addrandompart(20)
            if event.type == KEYDOWN and event.key == K_v:
                if settings.debugkeys:
                    wpos = vista.screentoworld(mousepos)
                    print("Visibility:", game.state.body.mask.visibility(wpos))
            if event.type == KEYUP and event.key == K_x:
                if settings.debugkeys:
                    if self.target is not None:
                        self.target.die()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.clickat = event.pos
            if event.type == MOUSEBUTTONUP and event.button == 1:
                self.handleleftclick(mousepos)
            if event.type == MOUSEBUTTONUP and event.button == 3:
                self.handlerightclick(mousepos)
            if event.type == MOUSEBUTTONUP and event.button == 4 and settings.zoomonscroll:
                vista.zoomin()
            if event.type == MOUSEBUTTONUP and event.button == 5 and settings.zoomonscroll:
                vista.zoomout()
            if event.type == MOUSEMOTION and event.buttons[0]:
                self.handleleftdrag(event.pos, event.rel)

        if settings.showtips:
            tip.settip(self.choosetip(mousepos))

        if keys[K_F5] and settings.debugkeys:
            game.state.body.addrandompart()

        if (keys[K_x] and settings.debugkeys) or self.cutmode:
            newtarget = self.pointchildbyedge(mousepos)
            if newtarget != self.target:
                if self.target is not None:
                    self.target.setbranchstatus()
                self.target = newtarget
                if self.target is not None:
                    self.target.setbranchstatus("target")
        elif self.healmode:
            game.state.body.sethealstatus()
            self.target = game.state.body.nearestorgan(vista.screentoworld(mousepos))
        elif self.target is not None:
            self.target.setbranchstatus()
            self.target = None

        vista.think(dt, mousepos, keys)
        vista.icons["cut"].selected = self.cutmode
        vista.icons["heal"].selected = self.healmode

        game.state.think(dt)
        status.state.think(dt)
        tip.think(dt)

    def clearselections(self, clearpanel = True, clearstatus = True, clearheal = True, clearcut = True):
        if self.target is not None:
            self.target.setbranchstatus()
        self.target = None
        self.parttobuild = None
        self.iconclicked = None
        panels.selecticon()
        if clearheal:
            if self.healmode:
                game.state.body.core.setbranchstatus()
            self.healmode = False
        if clearcut:
            self.cutmode = False

    def handleleftclick(self, mousepos):
        # TODO: handle dragging vs clicking more reliably
        if self.clickat is None:  # It's a drag
            return
        (x0, y0), (x1, y1) = self.clickat, mousepos
        if abs(x0-x1) + abs(y0-y1) > 25:
            return
    
        vicon = vista.iconhit(mousepos)  # Any vista icons pointed to
        if vicon is not None:
            self.handleiconclick(vicon)
            return

        bicon = panels.iconpoint(mousepos)  # Any panel tile or icon pointed to
        if bicon is not None:
            panels.selecticon(bicon)
            return


        # Click on the main gameplay area
        if vista.vrect.collidepoint(mousepos):
            if self.cutmode and self.target is not None:
                self.target.die()
                self.clearselections()
            elif self.healmode and self.target is not None:
                self.target.autoheal = not self.target.autoheal
            elif self.parttobuild is not None and self.canbuild and game.state.body.canaddpart(self.parttobuild):
                if panels.selectedtile is not None:
                    panels.claimtile()
                if panels.selectedorgan is not None:
                    panels.claimorgan()
                game.state.body.addpart(self.parttobuild)
                self.clearselections()
            else:
                worldpos = vista.screentoworld(mousepos)
                if vista.HexGrid.nearesttile(worldpos) == (0,0):
                    settings.showtips = not settings.showtips
                    noise.play("addpart")
            return
        
        # Click on one of the panels
        self.clearselections()


    def handleiconclick(self, vicon):
        if vicon == "trash":
            if panels.selectedtile is not None:
                panels.claimtile()
                self.clearselections()
        elif vicon == "zoomin":
            vista.zoomin()
        elif vicon == "zoomout":
            vista.zoomout()
        elif vicon == "menu":
            game.save()
            context.push(menu.Menu())
        elif vicon == "music":
            noise.nexttrack()
        elif vicon == "heal":
            game.state.body.core.setbranchstatus()
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
        

    def choosetip(self, mousepos):
        bicon = panels.iconpoint(mousepos)  # Any build icons pointed to
        vicon = vista.iconhit(mousepos)  # Any vista icons pointed to
        if vicon == "trash":
            if panels.selectedtile is not None:
                return "want to get rid of the stalk option? click here!"
            else:
                return "want to get rid of a stalk option? click on the stalk, then click here! you can also right-click on the stalk option"
        elif vicon == "zoomin":
            return
        elif vicon == "zoomout":
            return
        elif vicon == "menu":
            return "click to pause or quit game and pick options. it okay. me wait"
        elif vicon == "music":
            return "click to hear new song or turn songs off"
        elif vicon == "heal":
            if self.healmode:
                return "green organs will heal themself with ooze. red organs won't. click on organs you want to change"
            return "me organs will use ooze to heal when they get hurt. if you want some organs not to take ooze, click here to change them"
        elif vicon == "cut":
            return "you no like a stalk or a organ on me body? use this to get rid of it! it okay, me not get hurt"
        elif bicon is not None:
            if bicon in range(mechanics.ntiles):
                return "these me stalk options, har har har! can grow stalks where colors match, and can make stalks cross each other. try to make lots of branches."
            elif bicon == "ncube":
                return "the more me have of that organ, the faster the new stalks come"
            elif bicon == "control":
                return "me need brains to grow. the more brains me have, the more organs me can have"
            elif bicon == "mutagenmeter":
                return "that show how much mutagen me have. me like mutagen. it let me grow"
            elif bicon == "oozemeter":
                return "that show how much ooze me have. hurt organs will use ooze to heal selfs"
            elif bicon in mechanics.info:
                return mechanics.info[bicon]
            return None
        elif vista.vrect.collidepoint(mousepos):
            worldpos = vista.screentoworld(mousepos)
            if vista.HexGrid.nearesttile(worldpos) == (0,0):
                return "click me mouth to turn me tips on or off"
            # TODO: help on pointing to organs?
#            organ = game.state.body.nearestorgan(worldpos)

    def handlerightclick(self, mousepos):
        if vista.prect.collidepoint(mousepos):  # Click on panel
            self.clearselections()
            if settings.trashonrightclick:
                jtile = panels.iconpoint(mousepos)
                if jtile in range(mechanics.ntiles):
                    panels.claimtile(jtile)
                    noise.play("trash")
        elif vista.vrect.collidepoint(mousepos):  # Click on main window
            if settings.panonrightclick:
                vista.jumptoscreenpos(mousepos)
            else:
                self.clearselections()

    def handleleftdrag(self, pos, rel):
        if self.clickat is not None:
            (x0, y0), (x1, y1) = self.clickat, pos
            if abs(x0-x1) + abs(y0-y1) > 25:
                self.clickat = None

        if settings.panondrag:
            if vista.vrect.collidepoint(pos):
                vista.scoot(rel)


    def pointchildbyedge(self, screenpos):
        edge = vista.grid.nearestedge(vista.screentoworld(screenpos))
        edge = vista.grid.normedge(*edge)
        if edge not in game.state.body.takenedges:
            return None
        parent = game.state.body.takenedges[edge]
        if edge not in parent.buds:
            edge = vista.grid.opposite(*edge)
        return parent.buds[edge]
        

    def draw(self):
        vista.clear()
        game.state.draw()
        panels.draw()
        if self.parttobuild is not None:
            self.parttobuild.draw()
        vista.flip()


