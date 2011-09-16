import pygame, math
from pygame.locals import *
import vista, graphics, mechanics, font, settings


class Meter(object):
    left = 30
    def __init__(self):
        self.maxheight = 300
        self.height = 5
        self.goalheight = 5
        self.baseimg = self.getimg(self.height)
        self.bottom = self.left, self.maxheight + 40
        self.amount = 0

    def setheight(self, height):
        if height == self.goalheight: return
        self.goalheight = min(height, self.maxheight)
        if self.amount > self.goalheight:
            self.amount = self.goalheight

    def getimg(self, height):
        return graphics.helixmeter(height)

    def think(self, dt):
        self.amount = min(self.amount + dt * self.rate, self.goalheight)
        dh = self.goalheight - self.height
        if not dh: return
        if abs(dh) < 50 * dt:
            self.height = self.goalheight
        elif dh > 0:
            self.height += 50 * dt
        elif dh < 0:
            self.height -= 50 * dt
        self.baseimg = self.getimg(self.height)

    def meterpos(self, amount):
        """pixel coordinates corresponding to an amount on this meter"""
        return self.bottom[0], self.bottom[1] - self.getlevel(amount)
    
    def getlevel(self, amount = None):
        if amount is None: amount = self.amount
        return int(max(min(amount, self.height), 0))
    
    def draw(self):
        level = self.getlevel()
        img = graphics.meter(self.baseimg, level, self.color)
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
        self.currentrect = self.currentimg.get_rect(midright = (x-self.amount % 50,y))
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
    rate = mechanics.basemutagenrate
    color = graphics.colors["mutagen"]
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

class HealMeter(Meter):
    rate = mechanics.basehealrate
    color = graphics.colors["plaster"]

    left = 90

    def getimg(self, height):
        return graphics.stalkmeter(height)

    def think(self, dt):
        Meter.think(self, dt)
        vista.icons["heal"].active = self.amount > 10

def toscreen(rect):
    return rect.move(settings.rx0, settings.ry0)

def haspoint(rect, point):
    return toscreen(rect).collidepoint(point)



class Status(object):
    """Handles logic for the right-hand status panel"""
    def __init__(self, body):
        self.mutagenmeter = MutagenMeter()
        self.healmeter = HealMeter()
        self.body = body
        self.selected = None
        self.control = 5
        self.maxcontrol = 10
        self.brainimg = graphics.brain.img(zoom = 40)
        self.brainrect = self.brainimg.get_rect(bottomleft = (0, 480+6))

    def setheights(self, mutagenheight, healheight):
        self.mutagenmeter.setheight(mutagenheight)
        self.healmeter.setheight(healheight)

    def select(self, name = None):
        self.selected = name if name != self.selected else None

    def build(self):
        assert self.selected
        self.mutagenmeter.amount -= mechanics.costs[self.selected]
        self.select()

    def usehp(self, dhp):
        self.healmeter.amount -= dhp

    def think(self, dt, mousepos):
        self.mutagenmeter.think(dt)
        self.healmeter.think(dt)
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
        self.healmeter.draw()
        
        # Draw control tally
        if self.body.control >= self.body.maxcontrol:
            color, size = (128, 0, 0), 48
        else:
            color, size = (0,0,0), 32
        controlimg = font.img("%s/%s" % (self.body.control, self.body.maxcontrol), size=size, color=color)
        vista.rsurf.blit(self.brainimg, self.brainrect)
        vista.rsurf.blit(controlimg, controlimg.get_rect(midleft = self.brainrect.midright))



