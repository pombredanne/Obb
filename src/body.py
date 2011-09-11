import pygame
import vista

class Body(object):
    def __init__(self):
        self.core = Core(self, (0, 0))
        self.parts = [self.core]
    
    def draw(self):
        for part in self.parts:
            part.draw()

class BodyPart(object):
    def __init__(self, body, (x,y), edge = 0):
        self.body = body
        self.x, self.y = x, y
        self.edge = edge  # Edge number of base

class Core(BodyPart):
    """The central core of the body, that has the funny mouth"""
    def draw(self):
        px, py = vista.grid.gcenter((self.x, self.y))
        r = int(vista.grid.a * 0.8)
        pygame.draw.circle(vista.screen, (0, 192, 96), (px, py), r)



