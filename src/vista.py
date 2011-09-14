import pygame, math, datetime
from pygame.locals import *
import settings

# Okay, here's the deal. There are six simultaneous coordinate systems
#   going on at once.

# World coordinates: Zoom-level invariant coordinate system, where the
#   gameplay happens. Distances between game object should be computed
#   in this coordinate system.
# Hex coordinates: A skewed linear transform of world coordinates that
#   maps the tile centers to (integer) lattice points. Since edges are
#   midpoints between these, edges are obviously at half-integer
#   coordinates.
# Gameplay coordinates: Transformation of world coordinates to pixel
#   coordinates. The pixels in question are in some arbitrary surface
#   that doesn't necessarily correspond to the screen. The gameplay
#   surface can be resized when the gameplay area is extended, or when
#   the zoom level is changed. When these happen, the mapping to world
#   coordinates changes. Panning does not affect this mapping.
# View coordinates: The viewport is a rectangle that actually appears
#   on the screen. Generally it's a piece of the gameplay surface. The
#   mapping between gameplay coordinates and view coordinates can change
#   when the gameplay area is panned.
# Screen coordinates: The viewport doesn't have to be in the upper-left
#   corner of the window, in which case this coordinate system is used
#   for mouse coordinates and there's a transformation to view
#   coordinates that's just an offset.
# Mask coordinates: The mask is the surface that has the visibility-
#   blocking mask. It doesn't need very high resolution.

def init():
    global screen, _screen, vrect, prect, zoom, psurf
    flags = FULLSCREEN | HWSURFACE if settings.fullscreen else 0
    screen = pygame.Surface(settings.size, SRCALPHA)
    psurf = pygame.Surface(settings.psize, SRCALPHA)
    _screen = pygame.display.set_mode(settings.size, flags)
    # TODO: decouple view and screen coordinates
    vrect = pygame.Rect(settings.vx0, settings.vy0, settings.vx, settings.vy)
    prect = pygame.Rect(settings.px0, settings.py0, settings.px, settings.py)

wx0, wy0, wx1, wy1 = -6, -6, 6, 6  # Maximum extent of gameplay window
zoom = max(settings.zooms)
gx0, gy0 = 0, 0  # Gameplay location of world coordinate (0,0)

def setgrect((x0, y0, x1, y1)):
    global wx0, wy0, wx1, wy1, gx0, gy0, zoom
    wx0, wy0, wx1, wy1 = x0, y0, x1, y1

def zoomin():
    global zoom
    zs = [z for z in settings.zooms if z > zoom]
    if zs:
        zoom = min(zs)
def zoomout():
    global zoom
    zs = [z for z in settings.zooms if z < zoom]
    if zs:
        zoom = max(zs)

def think(dt, (mx, my)):
    global gx0, gy0
    xmin, xmax = vrect.width - wx1 * zoom, -wx0 * zoom
    ymin, ymax = vrect.height + wy0 * zoom, wy1 * zoom
    f = math.exp(-0.5 * dt)
    if vrect.collidepoint(mx,my) and pygame.mouse.get_focused():
        mx, my = mx - vrect.left, my - vrect.top
        # Potentially set the window based on mouse position
        if xmin < xmax:
            gx0 = xmax + (xmin - xmax) * mx / vrect.width
        else:
            dx = (xmin + xmax) / 2 - gx0
            gx0 += dx * f
        if ymin < ymax:
            gy0 = ymax + (ymin - ymax) * my / vrect.height
        else:
            dy = (ymin + ymax) / 2 - gy0
            gy0 += dy * f
    else:
        if xmin < xmax:
            dx = min(max(vrect.width/2, xmin), xmax) - gx0  # TODO: integer math
            gx0 += dx * f
        else:
            dx = (xmin + xmax) / 2 - gx0
            gx0 += dx * f
        if ymin < ymax:
            dy = min(max(vrect.height/2, ymin), ymax) - gy0
            gy0 += dy * f
        else:
            dy = (ymin + ymax) / 2 - gy0
            gy0 += dy * f


def worldtogameplay((x, y)):
    return int(gx0 + x * zoom + 0.5), int(gy0 - y * zoom + 0.5)

def gameplaytoworld((gx, gy)):
    return float(gx - gx0) / zoom, -float(gy - gy0) / zoom

def worldtoview((x, y)):
    return worldtogameplay((x, y))  # TODO

def screentoworld((x, y)):
    return gameplaytoworld((x, y))  # TODO

def clear(color = (64, 64, 64)):
    screen.fill(color)
    psurf.fill((64, 64, 0))

def screencap():
    dstr = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pygame.image.save(_screen, "screenshots/screenshot-%s.png" % dstr)

def addmask(mask):
    x0, y0 = gameplaytoworld((0, vrect.height))  # Bottom left world coordinates
    x1, y1 = gameplaytoworld((vrect.width, 0))   # Top right world coordinates
    gsx, gsy = worldtogameplay((wx1, wy0))
    screen.blit(mask.getmask((x0, y0, x1, y1), vrect.size), (0,0))

def flip():
#    screen.blit(gsurf)  # TODO
    _screen.blit(screen, vrect)
    _screen.blit(psurf, prect)
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
    def edgehex((x, y), e):
        """Hex coordinates of given edge"""
        dx, dy = [(0,0.5), (0.5,0), (0.5,-0.5),
                  (0,-0.5), (-0.5,0), (-0.5,0.5)][e%6]
        return x+dx, y+dy

    @staticmethod
    def edgeworld((x, y), e):
        """World coordinates of given edge"""
        return HexGrid.hextoworld(HexGrid.edgehex((x, y), e))

    @staticmethod
    def worldtohex((x, y)):
        """Convert hex coordinates to world coordinates"""
        return 2./3 * x, -x/3. + y/s3

    @staticmethod
    def hextoworld((x, y)):
        """Convert world coordinates to hex coordinates"""
        return 3./2 * x, s3*(x/2. + y)

    @staticmethod
    def opposite((x, y), e):
        """The tile and edge that's opposite the specified edge"""
        dx, dy = [(0,1), (1,0), (1,-1), (0,-1), (-1,0), (-1,1)][e%6]
        return (x+dx, y+dy), (e+3)%6

    @staticmethod
    def normedge(p, e):
        """The "normalized" edge, used for comparison"""
        return (p,e%6) if e%6 < 3 else HexGrid.opposite(p, e)

    @staticmethod
    def nearesttile(pos):
        """Tile that the given world coordinate is over"""
        hx, hy = [int(math.floor(p)) for p in HexGrid.worldtohex(pos)]
        d2 = lambda (x0, y0), (x1, y1): (x0 - x1) ** 2 + (y0 - y1) ** 2
        d2s = [(d2(pos, HexGrid.hextoworld((ax, ay))), (ax, ay))
                for ax in (hx,hx+1) for ay in (hy,hy+1)]
        return min(d2s)[1]

    @staticmethod
    def nearestedge(pos):
        """Nearest edge to given world coordinate (not normalized)"""
        tile = HexGrid.nearesttile(pos)
        d2 = lambda (x0, y0), (x1, y1): (x0 - x1) ** 2 + (y0 - y1) ** 2
        d2s = [(d2(pos, HexGrid.edgeworld(tile, edge)), (tile, edge))
                for edge in range(6)]
        return min(d2s)[1]

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


