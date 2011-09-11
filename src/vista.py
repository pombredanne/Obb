import pygame, math
from pygame.locals import *
import settings

screen = None

def init():
    global screen
    flags = FULLSCREEN if settings.fullscreen else 0
    screen = pygame.display.set_mode(settings.size, flags)

def clear(color = (64, 64, 64)):
    screen.fill(color)

def screencap():
    pygame.image.save(screen, "screenshot.png")


s3 = math.sqrt(3.)
class HexGrid(object):
    def __init__(self, p0 = None, a = 60):
        self.a = a  # circumradius of tile
        if p0 is None: p0 = settings.sx / 2, settings.sy / 2
        self.x0, self.y0 = p0
        
    def gcenter(self, (x, y)):
        """Screen coordinate of center of tile at (x,y)"""
        px = self.x0 + 1.5 * x * self.a
        py = self.y0 - s3 * (y + 0.5 * x) * self.a
        return int(px + .5), int(py + .5)

    def gvertex(self, (x, y), v):
        """Screen coordinate of vth vertex of tile at (x,y)"""
        dx, dy = [(0.5,-0.5), (1,0), (0.5,0.5),
                  (-0.5,0.5), (-1,0), (-0.5,-0.5)][v%6]
        px = self.x0 + (1.5 * x + dx) * self.a
        py = self.y0 - s3 * (y + 0.5 * x + dy) * self.a
        return int(px + .5), int(py + .5)

    def gedge(self, (x, y), e):
        """Screen coordinate of center of eth edge of tile at (x,y)"""
        dx, dy = [(0,-0.5), (0.75,-0.25), (0.75,0.25),
                  (0,0.5), (-0.75,0.25), (-0.75,-0.25)][e%6]
        px = self.x0 + (1.5 * x + dx) * self.a
        py = self.y0 - s3 * (y + 0.5 * x + dy) * self.a
        return int(px + .5), int(py + .5)

    def opposite(self, (x, y), e):
        """The tile and edge that's opposite the specified edge"""
        dx, dy = [(0,1), (1,0), (1,-1), (0,-1), (-1,0), (-1,1)][e%6]
        return (x+dx, y+dy), (e+3)%6

    def tnearest(self, (px, py)):
        """The tile that the given screen position is over"""
        x0 = math.floor(float(px - self.x0) / self.a / 1.5)
        y0 = math.floor(-float(py - self.y0) / self.a / s3 - 0.5 * x0)
        d2 = lambda (x0, y0), (x1, y1): (x0 - x1) ** 2 + (y0 - y1) ** 2
        d2s = [(d2((px, py), self.gcenter((x, y))), (x, y))
                for x in (x0,x0+1) for y in (y0,y0+1)]
        return min(d2s)[1]

    def drawhex(self, (x, y), color=None):
        if color is None:
            color = [(64,0,0),(0,64,0),(0,0,64)][(y-x)%3]
        vs = [self.gvertex((x, y), v) for v in range(6)]        
        pygame.draw.polygon(screen, color, vs)

grid = HexGrid()


