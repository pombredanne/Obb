import pygame
from pygame.locals import *
import vista, graphics


class Meter(object):
    def __init__(self):
        self.maxheight = 400
        self.height = 200
        self.baseimg = self.getimg(self.height)
        self.bottom = 30, self.maxheight + 40
        self.amount = 0
        self.rate = 1.

    def getimg(self, height):
        img = vista.Surface(60, 2*height)
        graphics.drawgrayhelix(img, (30, 2*height), (30, 0))
        return pygame.transform.smoothscale(img, (30, height))

    def think(self, dt):
        self.amount += dt * self.rate
    
    def getlevel(self):
        return int(self.amount)
    
    def draw(self):
        level = self.getlevel()
        img = graphics.meter(self.baseimg, level)
        vista.rsurf.blit(img, img.get_rect(midbottom = self.bottom))
        
        

class Status(object):
    """Handles logic for the right-hand status panel"""
    def __init__(self):
        self.meters = [Meter()]
    
    def think(self, dt):
        for meter in self.meters:
            meter.think(dt)
    
    def draw(self):
        for meter in self.meters:
            meter.draw()



