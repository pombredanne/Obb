import pygame, math
from pygame.locals import *
import vista, graphics, mechanics, font, settings


class Meter(object):
    def __init__(self):
        self.maxheight = 1000
        self.height = 60
        self.goalheight = 60
        self.baseimg = self.getimg(self.getlevel(self.height, False))
        self.bottom = self.left, settings.layout.meterbottom
        self.rect = self.baseimg.get_rect(midbottom = self.bottom)
        self.amount = 60

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
        self.baseimg = self.getimg(self.getlevel(self.height, False))
        self.rect = self.baseimg.get_rect(midbottom = self.bottom)

    def meterpos(self, amount, bounded = True):
        """pixel coordinates corresponding to an amount on this meter"""
        return self.bottom[0], self.bottom[1] - self.getlevel(amount, bounded)
    
    def getlevel(self, amount = None, bounded = True):
        if amount is None: amount = self.amount
        if bounded: amount = min(amount, self.height)
        return int(self.maxheight * (1 - math.exp(-2. * amount / self.maxheight)))
    
    def draw(self):
        level = self.getlevel()
        img = graphics.meter(self.baseimg, level, self.color)
        vista.rsurf.blit(img, self.rect)

class BuildIcon(object):
    def __init__(self, meter, name, number):
        self.meter = meter
        self.name = name
        self.img = graphics.icon(self.name)
        self.ghost = graphics.ghostify(self.img)
        self.amount = mechanics.costs[self.name]
        self.active = None  # Enough mutagen to activate
        self.visible = False
        self.currentimg = self.img
        self.pointedto = False
        number %= len(settings.layout.buildiconxs)
        self.x = settings.layout.buildiconxs[number]
        _, self.y = self.meter.meterpos(self.amount, bounded = False)
        self.rect = self.currentimg.get_rect(center = (self.x, self.y))

    def think(self, dt):
        active = self.meter.amount >= self.amount
        self.visible = self.meter.height >= self.amount
        if self.active is False and active:
            self.activate()
        self.active = active
        self.currentimg = self.img if self.active else self.ghost
#       self.linepos = x,y = self.meter.meterpos(self.amount)
        self.pointedto = False

    def ispointedto(self, pos):
        return self.active and self.rect.collidepoint(pos)

    def activate(self):
        pass

    def draw(self):
#        x,y = self.linepos
#        pygame.draw.line(vista.rsurf, (255, 255, 255), (x-20,y), (x,y))
        if self.visible:
            vista.addoverlay(self.currentimg, self.rect)
        

class MutagenMeter(Meter):
    rate = mechanics.basemutagenrate
    color = graphics.colors["mutagen"]
    left = settings.layout.mutagenmeterx
    def __init__(self):
        Meter.__init__(self)
        inames = [(value, key) for key, value in mechanics.costs.items()]
        inames.sort()
        self.icons = [BuildIcon(self, name, j) for j, (cost, name) in enumerate(inames)]

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
    left = settings.layout.healmeterx

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
        self.brainimg = graphics.brain.img(zoom = settings.layout.organcountsize)
        self.brainrect = self.brainimg.get_rect(bottomleft = settings.layout.brainiconpos)
        self.controlrect = self.brainrect

    def setheights(self, mutagenheight, healheight):
        self.mutagenmeter.setheight(mutagenheight)
        self.healmeter.setheight(healheight)

    def select(self, name = None):
        self.selected = name if name != self.selected else None

    def build(self):
        assert self.selected
        self.mutagenmeter.amount -= mechanics.costs[self.selected]
        self.select()

#    def usehp(self, dhp):
#        self.healmeter.amount -= dhp

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
        color, size = (0,0,0), settings.layout.countsize
        if self.body.control >= self.body.maxcontrol:
            color, size = (128, 0, 0), int(size * 1.5)
        controlimg = font.img("%s/%s" % (self.body.control, self.body.maxcontrol), size=size, color=color)
        vista.rsurf.blit(self.brainimg, self.brainrect)
        self.controlrect = controlimg.get_rect(midleft = settings.layout.controlpos)
        vista.rsurf.blit(controlimg, self.controlrect)

    def choosetip(self, (mx, my)):
        mousepos = mx - settings.rx0, my - settings.ry0
        if self.mutagenmeter.rect.collidepoint(mousepos):
            return "that show how much mutagen me have. me like mutagen. it let me grow"
        if self.healmeter.rect.collidepoint(mousepos):
            return "that show how much ooze me have. ooze let me fix organs when they get broke"
        if self.brainrect.collidepoint(mousepos) or self.controlrect.collidepoint(mousepos):
            return "me need brains to grow. the more brains me have the more organs me can have"
        



