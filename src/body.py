import pygame, random
from pygame.locals import *
import vista, mask, graphics, mechanics

class Body(object):
    def __init__(self, (x, y) = (0, 0)):
        self.parts = []
        self.takentiles = {}
        self.takenedges = {}
        self.takenbuds = {}
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
            r = random.random()
            if r < 0.7:
                appspec = mechanics.randomspec()
                part = Appendage(self, parent, pos, edge, appspec)
            elif r < 0.8:
                part = Eye(self, parent, pos, edge)
            elif r < 0.9:
                part = Leaf(self, parent, pos, edge)
            else:
                part = Mutagenitor(self, parent, pos, edge)
            if part.color != parent.budcolors[bud]: continue
            if not self.canaddpart(part): continue
            self.addpart(part)
            added += 1
            if added == n: return n
        return added

    def canplaceapp(self, edge, appspec):
        """If you can place the specified app on the specified edge,
        return the corresponding part. Otherwise return None"""
        for bud in (edge, vista.HexGrid.opposite(*edge)):
            if bud not in self.takenbuds: continue
            parent = self.takenbuds[bud]
            if parent.buds[bud] is not None: continue
            part = Appendage(self, parent, bud[0], bud[1], appspec)
            if part.color != parent.budcolors[bud]: continue
            return part
        return None

    def canplaceorgan(self, edge, otype):
        """If you can place the specified organ type on the specified edge,
        return the corresponding part. Otherwise return None"""
        otypes = {"eye": Eye}
        if isinstance(otype, str): otype = otypes[otype]
        for bud in (edge, vista.HexGrid.opposite(*edge)):
            if bud not in self.takenbuds: continue
            parent = self.takenbuds[bud]
            if parent.buds[bud] is not None: continue
            if otype.color != parent.budcolors[bud]: continue
            part = otype(self, parent, bud[0], bud[1])
            return part
        return None

    def canaddpart(self, part):
        tiles, edges = part.claimedsets()
        if any(tile in self.takentiles for tile in tiles): return False
        if any(edge in self.takenedges for edge in edges): return False
        return True

    def addpart(self, part):
        assert self.canaddpart(part)
        self.parts.append(part)
        if part.parent is not None:
            part.parent.buds[((part.x, part.y), part.edge)] = part
        part.status = ""
        tiles, edges = part.claimedsets()
        for tile in tiles: self.takentiles[tile] = part
        for edge in edges: self.takenedges[edge] = part
        for bud in part.buds: self.takenbuds[bud] = part
        if part.lightradius > 0 and self.mask is not None:
            self.mask.addp(*part.lightcircle())
            vista.setgrect(self.mask.bounds())

    def remakemask(self):
        """Build the mask from scratch"""
        circles = [part.lightcircle() for part in self.parts if part.lightradius > 0]
        self.mask = mask.Mask(circles)

    def removepart(self, part):
        """This is like the manual override. Shouldn't be called directly.
        Instead call part.die()"""
        assert not isinstance(part, Core)
        self.parts.remove(part)
        edge = (part.x, part.y), part.edge
        assert part.parent.buds[edge] is part
        part.parent.buds[edge] = None
        tiles, edges = part.claimedsets()
        for tile in tiles: del self.takentiles[tile]
        for edge in edges: del self.takenedges[edge]
        for bud in part.buds: del self.takenbuds[bud]
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
        for part in self.parts:
            part.think(dt)
        if self.mask is None:
            self.remakemask()
            vista.setgrect(self.mask.bounds())
    
    def draw(self):
        for part in sorted(self.parts, key = lambda p: p.draworder):
            part.draw()

    def tracehexes(self, color = (128, 128, 128)):
        tiles = set([(part.x, part.y) for part in self.parts])
        for tile in tiles:
            vista.HexGrid.tracehex(tile, color)


class BodyPart(object):
    lightradius = 0  # How much does this part extend your visibility
    draworder = 0
    growtime = 0
    dietime = 0.1
    def __init__(self, body, parent, (x,y), edge = 0):
        self.body = body
        self.parent = parent
        self.x, self.y = x, y
        self.worldpos = vista.grid.hextoworld((self.x, self.y))
        self.edge = edge  # Edge number of base
        self.edgeworldpos = vista.grid.edgeworld((self.x, self.y), self.edge)
        self.buds = {}  # New body parts that are formed off this one
                        # (set to None if no body part there yet)
        self.lastkey = None
        self.budcolors = {}
        self.status = ""
        self.growtimer = self.growtime
        self.dietimer = None

    def think(self, dt):
        if self.growtimer > 0:
            if not self.parent or not self.parent.growtimer:
                self.growtimer = max(self.growtimer - dt, 0)
        elif self.dietimer is not None:
            candie = all(part is None for part in self.buds.values())
            if candie:
                self.dietimer -= dt
                if self.dietimer < 0:
                    self.body.removepart(self)

    def die(self):
        for part in self.buds.values():
            if part is not None:
                part.die()
        self.dietimer = self.dietime
        

    def setbranchstatus(self, status = ""):
        self.status = status
        for child in self.buds.values():
            if child is not None:
                child.setbranchstatus(status)

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

    def getkey(self):
        zoom = int(vista.zoom + 0.5)
        if self.dietimer is not None:
            growth = self.dietimer / self.dietime
        elif "ghost" in self.status:
            growth = 1
        elif self.growtimer:
            growth = 1 - self.growtimer / self.growtime
        else:
            growth = 1
        return zoom, self.status, growth

    def draw(self):
        key = self.getkey()
        if key != self.lastkey:
            self.lastkey = key
            self.img = self.draw0(*key)
        px, py = vista.worldtoview(vista.grid.hextoworld((self.x, self.y)))
        vista.screen.blit(self.img, self.img.get_rect(center = (px, py)))

    @staticmethod
    def colorbycode(colorcode):
        return [(0,192,64), (64,64,192), (160,80,0)][colorcode]

class Core(BodyPart):
    """The central core of the body, that has the funny mouth"""
    lightradius = 5
    growtime = 1.8
    def __init__(self, body, (x,y) = (0,0)):
        BodyPart.__init__(self, body, None, (x,y), 0)
        for edge in range(6):  # One bud in each of six directions
            oppedge = vista.grid.opposite((x, y), edge)
            self.buds[oppedge] = None
            self.budcolors[oppedge] = "app%s" % (edge % 3)

    def tiles(self):
        return ((self.x, self.y),)

    def draw0(self, zoom, status, growth):
        color = "core"
        return graphics.core(color, growth, zoom)

def qBezier((x0,y0), (x1,y1), (x2,y2), n = 6):
    """Quadratic bezier curve"""
    ts = [float(j) / n for j in range(n+1)]
    cs = [((1-t)**2, 2*t*(1-t), t**2) for t in ts]
    return [(a*x0+b*x1+c*x2, a*y0+b*y1+c*y2) for a,b,c in cs]    

class Appendage(BodyPart):
    """A stalk that leads to one or more subsequent buds"""
    draworder = 1
    growtime = 0.3
    def __init__(self, body, parent, (x,y), edge, appspec):
        BodyPart.__init__(self, body, parent, (x,y), edge)
        self.appspec = appspec
        self.color = appspec.color
        for bud in self.appspec.outbuds((x, y), edge):
            self.buds[bud] = None
            self.budcolors[bud] = self.color

    def draw0(self, zoom, status, growth):
        color = status or self.color
        segs =  int(8. * growth) if growth != 1 else 8
        if "ghost" in self.status: segs = 8
        return graphics.app(self.appspec.dedges, color, self.edge, zoom, segs = segs)
            
class Organ(BodyPart):
    """A functional body part that terminates a stalk"""
    draworder = 2
    growtime = 0.3
    def draw0(self, zoom, status, growth):
        color = status or self.color
        if growth != 1:
            segs = min(int(8. * growth), 3)
            R = int(max(20 * growth - 10, 0)) * 0.1
        else:
            segs, R = 3, 1
        return graphics.organ(0.5*R, color, self.edge, zoom = zoom, segs = segs)

    def tiles(self):
        return ((self.x, self.y),)

class Eye(Organ):
    """Extends your visible region"""
    lightradius = 5
    color = "app0"

    def __init__(self, *args, **kw):
        Organ.__init__(self, *args, **kw)
        self.tblink = 0

    def think(self, dt):
        Organ.think(self, dt)
        if self.tblink == 0 and random.random() * 4 < dt:
            self.tblink = 0.3
        if self.tblink:
            self.tblink = max(self.tblink - dt, 0)
        if self.growtimer:
            self.tblink = 0.45

    def getkey(self):
        blink = abs(self.tblink - 0.15) / 0.15 if self.tblink else 1
        while blink > 1.0001: blink = abs(blink - 2)
        if "ghost" in self.status: blink = 1
        return Organ.getkey(self) + (blink,)

    def draw0(self, zoom, status, growth, blink):
        if growth != 1:
            return Organ.draw0(self, zoom, status, growth)
        center = cx, cy = zoom, zoom
        color = status or self.color
        return graphics.eye(color, self.edge, blink, zoom = zoom)

class Leaf(Organ):
    """Collects light and generates energy"""
    color = "app1"

class Mutagenitor(Organ):
    """Collects light and generates mutagen"""
    color = "app2"



