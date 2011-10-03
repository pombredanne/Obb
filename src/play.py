import pygame, random
from pygame.locals import *
import vista, context, settings, noise, enemy, graphics, tip, mechanics, game

class Play(context.Context):
    def __init__(self):
        self.edgepoint = None
        self.paused = False
        self.target = None
        self.healmode = False
        self.clearselections()
        self.clickat = None

    def think(self, dt, events, keys, mousepos, buttons):

        if self.paused:
            if any(e.type == KEYDOWN or e.type == MOUSEBUTTONDOWN for e in events):
                self.resume()
            return


        if vista.vrect.collidepoint(mousepos):
            edge = vista.grid.nearestedge(vista.screentoworld(mousepos))
            if edge != self.edgepoint:
                if game.state.panel.selected is not None:
                    appspec = game.state.panel.tiles[game.state.panel.selected]
                    self.parttobuild = game.state.body.canplaceapp(edge, appspec)
                elif game.state.status.selected is not None:
                    otype = game.state.status.selected
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
                    print "Visibility:", game.state.body.mask.visibility(wpos)
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

        game.state.think(dt, mousepos)
        tip.think(dt)

    def pause(self):
        self.paused = True
        self.pscreen = graphics.ghostify(vista._screen.convert_alpha())
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
            game.state.panel.selecttile()
        if clearstatus:
            game.state.status.select()
        if clearheal:
            if self.healmode:
                game.state.body.core.setbranchstatus()
            self.healmode = False
        if clearcut:
            self.cutmode = False

    def handleleftclick(self, mousepos):

        if self.clickat is None:  # It's a drag
            return
        (x0, y0), (x1, y1) = self.clickat, mousepos
        if abs(x0-x1) + abs(y0-y1) > 25:
            return
    
        bicon = game.state.status.iconpoint(mousepos)  # Any build icons pointed to
        vicon = vista.iconhit(mousepos)  # Any vista icons pointed to
        if vicon == "trash":
            game.state.panel.trashtile()
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
        elif vista.prect.collidepoint(mousepos):  # Click on panel
            self.clearselections(clearpanel = False)
            jtile = game.state.panel.iconp(mousepos)
            if jtile in (None, 0, 1, 2, 3, 4, 5):
                game.state.panel.selecttile(jtile)
        elif bicon is not None:
            self.clearselections(clearstatus = False)
            game.state.status.select(bicon.name)
        elif vista.vrect.collidepoint(mousepos):
            if self.cutmode and self.target is not None:
                self.target.die()
                self.clearselections()
            elif self.healmode and self.target is not None:
                self.target.autoheal = not self.target.autoheal
            elif self.parttobuild is not None and self.canbuild and game.state.body.canaddpart(self.parttobuild):
                if game.state.panel.selected is not None:
                    game.state.panel.claimtile()
                if game.state.status.selected is not None:
                    game.state.status.build()
                game.state.body.addpart(self.parttobuild)
                self.clearselections()
            else:
                worldpos = vista.screentoworld(mousepos)
                if vista.HexGrid.nearesttile(worldpos) == (0,0):
                    settings.showtips = not settings.showtips
                    noise.play("addpart")

    def choosetip(self, mousepos):
        bicon = game.state.status.iconpoint(mousepos)  # Any build icons pointed to
        vicon = vista.iconhit(mousepos)  # Any vista icons pointed to
        if vicon == "trash":
            if games.state.panel.selected is not None:
                return "click this to get rid of stalk and get new one"
            else:
                return "if you no like a stalk, click on stalk then click here to get new one. or you can right-click on stalk, it faster"
        elif vicon == "zoomin":
            return
        elif vicon == "zoomout":
            return
        elif vicon == "pause":
            return "click to pause game. it okay. me wait"
        elif vicon == "music":
            return "click to hear new song or turn off"
        elif vicon == "heal":
            if self.healmode:
                return "click on organs to change them so they don't heal by self. no want to waste ooze on non-vital organs"
            return "me organs will use ooze to heal when they get hurt. if you want some organs not to take ooze, click here to change them"
        elif vicon == "cut":
            return "no like a stalk or a organ on me body? use this to get rid of it! it okay, me not get hurt"
        elif vista.prect.collidepoint(mousepos):
            jtile = game.state.panel.iconp(mousepos)
            if jtile in (0, 1, 2, 3, 4, 5):
                return "these me stalk options, har har har! can grow stalks where colors match. try make lots of branches."
            else:
                return game.state.panel.choosetip(mousepos)
        elif bicon is not None:
            return mechanics.info[bicon.name]
        elif vista.vrect.collidepoint(mousepos):
            worldpos = vista.screentoworld(mousepos)
            if vista.HexGrid.nearesttile(worldpos) == (0,0):
                return "click me mouth to turn me tips on or off"
            # TODO: help on pointing to organs?
#            organ = game.state.body.nearestorgan(worldpos)
        elif vista.rrect.collidepoint(mousepos):
            return game.state.status.choosetip(mousepos)

    def handlerightclick(self, mousepos):
        if vista.prect.collidepoint(mousepos):  # Click on panel
            self.clearselections()
            if settings.trashonrightclick:
                jtile = game.state.panel.iconp(mousepos)
                if jtile in (0, 1, 2, 3, 4, 5):
                    game.state.panel.selecttile(jtile)
                    game.state.panel.claimtile()
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
        if self.paused:
            vista._screen.blit(self.pscreen, (0,0))
            pygame.display.flip()
            return
        vista.clear()
        game.state.draw()
        if self.parttobuild is not None:
            self.parttobuild.draw()
        vista.flip()


