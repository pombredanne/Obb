import pygame, math
from pygame.locals import *
import vista, graphics, mechanics, font


class Meter(object):
    def __init__(self):
        self.maxheight = 300
        self.height = 200
        self.baseimg = self.getimg(self.height)
        self.bottom = 30, self.maxheight + 40
        self.amount = 0
        self.rate = mechanics.basemutagenrate

    def getimg(self, height):
        return graphics.helixmeter(height)

    def think(self, dt):
        self.amount = min(self.amount + dt * self.rate, self.height)

    def meterpos(self, amount):
        """pixel coordinates corresponding to an amount on this meter"""
        return self.bottom[0], self.bottom[1] - self.getlevel(amount)
    
    def getlevel(self, amount = None):
        if amount is None: amount = self.amount
        return int(max(min(amount, self.height), 0))
    
    def draw(self):
        level = self.getlevel()
        img = graphics.meter(self.baseimg, level, (0.7, 0, 1))
        vista.rsurf.blit(img, img.get_rect(midbottom = self.bottom))

class BuildIcon(object):
    def __init__(self, meter, name):
        self.meter = meter
        self.name = name
        self.img0 = graphics.icon(self.name)
        self.ghost0 = graphics.ghostify(self.img0)
        self.img = pygame.transform.rotozoom(self.img0, 0, 0.4)
        self.ghost = pygame.transform.rotozoom(self.ghost0, 0, 0.4)
        self.amount = mechanics.costs[self.name]
        self.focustimer = 0
        self.active = None  # Enough mutagen to activate
        self.currentimg = self.img
        self.currentrect = self.img.get_rect()
        self.pointedto = False

    def think(self, dt):
        active = self.meter.amount > self.amount
        if self.active is False and active:
            self.activate()
        self.active = active
        if self.focustimer:
            self.focustimer = max(self.focustimer - dt, 0)
        if self.pointedto or self.focustimer:
            self.currentimg = self.img0 if self.active else self.ghost0
        else:
            self.currentimg = self.img if self.active else self.ghost
        self.linepos = x,y = self.meter.meterpos(self.amount)
        self.currentrect = self.currentimg.get_rect(midright = (x-20,y))
        self.currentrect.move_ip(*vista.rrect.topleft)
        self.pointedto = False

    def ispointedto(self, pos):
        return self.active and self.currentrect.collidepoint(pos)

    def activate(self):
        self.focustimer = 2

    def draw(self):
        x,y = self.linepos
        pygame.draw.line(vista.rsurf, (255, 255, 255), (x-20,y), (x,y))
        vista.addoverlay(self.currentimg, self.currentrect)
        

class MutagenMeter(Meter):
    def __init__(self):
        Meter.__init__(self)
        self.icons = [BuildIcon(self, name) for name in mechanics.costs]

    def think(self, dt):
        Meter.think(self, dt)
        for icon in self.icons:
            icon.think(dt)

    def draw(self):
        for icon in self.icons:
            icon.draw()
        Meter.draw(self)


class Status(object):
    """Handles logic for the right-hand status panel"""
    def __init__(self, body):
        self.mutagenmeter = MutagenMeter()
        self.body = body
        self.selected = None
        self.control = 5
        self.maxcontrol = 10
        self.brainimg = graphics.brain.img(zoom = 40)
        self.brainrect = self.brainimg.get_rect(bottomleft = (0, 480+6))

    def select(self, name = None):
        self.selected = name if name != self.selected else None

    def build(self):
        assert self.selected
        self.mutagenmeter.amount -= mechanics.costs[self.selected]
        self.select()

    def think(self, dt, mousepos):
        self.mutagenmeter.think(dt)
        icon = self.iconpoint(mousepos)
        if icon is not None:
            icon.pointedto = True
        if self.selected is not None:
            for icon in self.mutagenmeter.icons:
                if icon.name == self.selected:
                    icon.pointedto = True

    def iconpoint(self, mousepos):
        for icon in self.mutagenmeter.icons:
            if icon.ispointedto(mousepos):
                return icon
        return None

    def draw(self):
        self.mutagenmeter.draw()
        
        if self.body.control >= self.body.maxcontrol:
            color, size = (128, 0, 0), 48
        else:
            color, size = (0,0,0), 32
        controlimg = font.img("%s/%s" % (self.body.control, self.body.maxcontrol), size=size, color=color)
        vista.rsurf.blit(self.brainimg, self.brainrect)
        vista.rsurf.blit(controlimg, controlimg.get_rect(midleft = self.brainrect.midright))



