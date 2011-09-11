import pygame, math, datetime
from pygame.locals import *
import settings

def init():
    global screen, _screen, vrect
    flags = FULLSCREEN if settings.fullscreen else 0
    screen = pygame.Surface(settings.size, SRCALPHA)
    _screen = pygame.display.set_mode(settings.size, flags)
    vrect = pygame.Rect(0, 0, settings.sx, settings.sy)

def clear(color = (64, 64, 64)):
    screen.fill(color)

def screencap():
    dstr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pygame.image.save(screen, "screenshots/screenshot-%s.png" % dstr)

def flip():
    _screen.blit(screen, vrect)
    pygame.display.flip()

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
        dx, dy = [(0,0.5), (0.75,0.25), (0.75,-0.25),
                  (0,-0.5), (-0.75,-0.25), (-0.75,0.25)][e%6]
        px = self.x0 + (1.5 * x + dx) * self.a
        py = self.y0 - s3 * (y + 0.5 * x + dy) * self.a
        return int(px + .5), int(py + .5)

    @staticmethod
    def opposite((x, y), e):
        """The tile and edge that's opposite the specified edge"""
        dx, dy = [(0,1), (1,0), (1,-1), (0,-1), (-1,0), (-1,1)][e%6]
        return (x+dx, y+dy), (e+3)%6

    @staticmethod
    def normedge(p, e):
        """The "normalized" edge, used for comparison"""
        return (p,e%6) if e%6 < 3 else HexGrid.opposite(p, e)

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

grid = HexGrid(a = 30)


class Mask(object):
    """A fog-of-war style mask (black with a variable alpha)"""
    circs = {}
    def __init__(self, (sx, sy), ps = (), color = (0, 0, 0), ):
        self.sx, self.sy = sx, sy
        self.color = tuple(color)
        self.ps = list(ps)
        self.draw()

    def draw(self):
        """Draw entire surface from scratch"""
        self.surf = pygame.Surface((self.sx, self.sy), SRCALPHA)
        self.surf.fill(self.color)
        self.blue = pygame.Surface((self.sx, self.sy), SRCALPHA)
        self.blue.fill((0,0,0))
        for p, r in self.ps:
            self.addcirc(p, r)
        self.alphacopy()

    def addp(self, p, r):
        self.ps.append((p, r))
        self.addcirc(p, r)
        self.alphacopy()

    def addcirc(self, (px, py), r):
        """Add a circle onto the blue surface"""
        self.blue.blit(self.getcirc(r), (px-r, py-r))

    def alphacopy(self):
        """Copy from pixel data in the blue surface to the alpha
        channel of the main surface"""
        pygame.surfarray.pixels_alpha(self.surf)[:,:] = 255 - pygame.surfarray.array2d(self.blue)
        
    @staticmethod
    def getcirc(r):
        if r not in Mask.circs:
            # TODO: pygame.surfarray
            img = pygame.Surface((2*r, 2*r), SRCALPHA)
            for x in range(2*r):
                for y in range(2*r):
                    d2 = float((x - r) ** 2 + (y - r) ** 2) / r ** 2
                    d = math.sqrt(d2)
                    a = max(min(int(255 * 1 / (1 + math.exp(-6 + 12 * d))), 255), 0)
                    img.set_at((x,y), (0, 0, 255, a))
            Mask.circs[r] = img
        return Mask.circs[r]
        


