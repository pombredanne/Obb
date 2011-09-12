import pygame, random
from pygame.locals import *
import vista, mask

class Body(object):
    def __init__(self, (x, y) = (0, 0)):
        self.parts = []
        self.takentiles = {}
        self.takenedges = {}
        self.core = Core(self, (x, y))
        self.mask = None
        self.addpart(self.core)

    def addrandompart(self, n = 1, maxtries = 100):
        added = 0
        for tries in range(maxtries):
            parent = random.choice(self.parts)
            bud = parent.randombud()
            if not bud: continue
            pos, edge = bud
            if random.random() < 0.8:
                appspec = randomspec()
                part = Appendage(self.core, parent, pos, edge, appspec)
            else:
                part = Eye(self.core, parent, pos, edge)
            if part.colorcode != parent.budcolors[bud]: continue
            if not self.canaddpart(part): continue
            parent.buds[bud] = part
            self.addpart(part)
            added += 1
            if added == n: return n
        return added

    def canaddpart(self, part):
        tiles, edges = part.claimedsets()
        if any(tile in self.takentiles for tile in tiles): return False
        if any(edge in self.takenedges for edge in edges): return False
        return True

    def addpart(self, part):
        assert self.canaddpart(part)
        self.parts.append(part)
        tiles, edges = part.claimedsets()
        for tile in tiles: self.takentiles[tile] = part
        for edge in edges: self.takenedges[edge] = part
        if part.lightradius > 0 and self.mask is not None:
            self.mask.addp(*part.lightcircle())
            vista.setgrect(self.mask.bounds())

    def remakemask(self):
        """Build the mask from scratch"""
        circles = [part.lightcircle() for part in self.parts if part.lightradius > 0]
        self.mask = mask.Mask(circles)

    def removepart(self, part):
        assert not isinstance(part, Core)
        self.parts.remove(part)
        edge = (part.x, part.y), part.edge
        assert part.parent.buds[edge] is part
        part.parent.buds[edge] = None
        tiles, edges = part.claimedsets()
        for tile in tiles: del self.takentiles[tile]
        for edge in edges: del self.takenedges[edge]
        assert part not in self.takentiles.values()
        assert part not in self.takenedges.values()
        if part.lightradius > 0:
            self.mask = None

    def removebranch(self, part):
        """Remove a part and all its children"""
        for child in part.buds.values():
            if child is not None:
                self.removebranch(child)
        self.removepart(part)

    def think(self, dt):
        if self.mask is None:
            self.remakemask()
            vista.setgrect(self.mask.bounds())
    
    def draw(self):
        for part in sorted(self.parts, key = lambda p: p.draworder):
            part.draw()

class BodyPart(object):
    lightradius = 0  # How much does this part extend your visibility
    draworder = 0
    def __init__(self, body, parent, (x,y), edge = 0):
        self.body = body
        self.parent = parent
        self.x, self.y = x, y
        self.worldpos = vista.grid.hextoworld((self.x, self.y))
        self.edge = edge  # Edge number of base
        self.edgeworldpos = vista.grid.edgeworld((self.x, self.y), self.edge)
        self.buds = {}  # New body parts that are formed off this one
                        # (set to None if no body part there yet)
        self.lastzoom = None
        self.budcolors = {}

    def lightcircle(self):
        return vista.grid.hextoworld((self.x,self.y)), self.lightradius

    def tiles(self):
        return ()
    
    def edges(self):
        return self.buds.keys()

    def claimedsets(self):
        ts = set(self.tiles())
        es = set(vista.grid.normedge(p, e) for p,e in self.edges())
        return ts, es

    def screenpos(self):
        return vista.worldtoview(self.worldpos)

    def edgescreenpos(self):
        return vista.worldtoview(self.edgeworldpos)

    @staticmethod
    def budscreenpos(p, e):
        """Screen position of a given edge"""
        return vista.worldtoview(vista.grid.edgeworld(p, e))

    def randombud(self):
        """Return a bud that hasn't been used yet"""
        buds = [key for key,value in self.buds.items() if value == None]
        if not buds: return None
        return random.choice(buds)

    def draw(self):
        zoom = int(vista.zoom + 0.5)
        if zoom != self.lastzoom:
            self.lastzoom = zoom
            self.img = pygame.Surface((2*zoom, 2*zoom), SRCALPHA)
            self.draw0(self.img, zoom, (zoom, zoom))
        px, py = vista.worldtoview(vista.grid.hextoworld((self.x, self.y)))
        vista.screen.blit(self.img, (px-zoom, py-zoom))

    @staticmethod
    def colorbycode(colorcode):
        return [(0,192,64), (128,0,128), (192,64,0)][colorcode]

class Core(BodyPart):
    """The central core of the body, that has the funny mouth"""
    lightradius = 8
    def __init__(self, body, (x,y) = (0,0)):
        BodyPart.__init__(self, body, None, (x,y), 0)
        for edge in range(6):  # One bud in each of six directions
            oppedge = vista.grid.opposite((x, y), edge)
            self.buds[oppedge] = None
            self.budcolors[oppedge] = edge % 3

    def tiles(self):
        return ((self.x, self.y),)

    def draw0(self, img, zoom, center):
        r = int(zoom * 0.85)
        pygame.draw.circle(img, (0, 192, 96), center, r)

class AppendageSpec(object):
    """Data to specify the path of an appendage, irrespective of starting position"""
    def __init__(self, dedges, colorcode):
        self.dedges = sorted(set(dedges))
        self.colorcode = colorcode
    
    def outbuds(self, pos, edge):
        return [vista.grid.opposite(pos, edge + dedge) for dedge in self.dedges]

def randomspec(n = 2):
    return AppendageSpec([random.choice(range(5))+1 for _ in range(n)], random.choice((0,1,2)))


def qBezier((x0,y0), (x1,y1), (x2,y2), n = 6):
    """Quadratic bezier curve"""
    ts = [float(j) / n for j in range(n+1)]
    cs = [((1-t)**2, 2*t*(1-t), t**2) for t in ts]
    return [(a*x0+b*x1+c*x2, a*y0+b*y1+c*y2) for a,b,c in cs]    

class Appendage(BodyPart):
    """A stalk that leads to one or more subsequent buds"""
    draworder = 1
    def __init__(self, body, parent, (x,y), edge, appspec):
        BodyPart.__init__(self, body, parent, (x,y), edge)
        self.appspec = appspec
        self.colorcode = appspec.colorcode
        self.color = self.colorbycode(self.colorcode)
        for bud in self.appspec.outbuds((x, y), edge):
            self.buds[bud] = None
            self.budcolors[bud] = self.colorcode

    def draw0(self, img, zoom, (cx, cy)):
        def hextooffset((x, y)):
            """Convert hex coordinates to offset within this image"""
            wx, wy = vista.grid.hextoworld((x, y))
            px = int(cx + zoom * wx + 0.5)
            py = int(cy - zoom * wy + 0.5)
            return px, py
        p0 = hextooffset(vista.grid.edgehex((0,0), self.edge))
        p1 = (cx, cy)
        for p, edge in self.buds:
            p2 = hextooffset(vista.grid.edgehex((0,0), edge + 3))
            ps = qBezier(p0, p1, p2)
            pygame.draw.lines(img, self.color, False, ps, int(vista.zoom * 0.3))
            
class Organ(BodyPart):
    """A functional body part that terminates a stalk"""
    draworder = 2
    def draw0(self, img, zoom, center):
        r = int(zoom * 0.5)
        pygame.draw.circle(img, (0, 192, 64), center, r)

    def tiles(self):
        return ((self.x, self.y),)

class Eye(Organ):
    """Extends your visible region"""
    lightradius = 8
    colorcode = 0

    def draw0(self, img, zoom, center):
        wx, wy = vista.grid.hextoworld(vista.grid.edgehex((0,0), self.edge))
        cx, cy = center
        p0 = int(cx + zoom * wx + 0.5), int(cy - zoom * wy + 0.5)
        color = self.colorbycode(self.colorcode)
        pygame.draw.line(img, color, p0, center, int(vista.zoom * 0.3))
        pygame.draw.circle(img, color, center, int(zoom * 0.5))
        pygame.draw.circle(img, (255, 255, 255), center, int(zoom * 0.4))
        pygame.draw.circle(img, (0, 0, 0), center, int(zoom * 0.2))


