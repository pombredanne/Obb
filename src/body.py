import pygame, random
import vista, mask

class Body(object):
    def __init__(self, (x, y) = (0, 0)):
        self.parts = []
        self.takentiles = set()
        self.takenedges = set()
        self.core = Core(self, (x, y))
        self.mask = mask.Mask((self.core.lightcircle(),))
        vista.setgrect(self.mask.bounds())
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
                part = Appendage(self.core, pos, edge, appspec)
            else:
                part = Eye(self.core, pos, edge)
            if not self.canaddpart(part): continue
            parent.buds[bud] = part
            self.addpart(part)
            added += 1
            if added == n: return n
        return added

    def canaddpart(self, part):
        tiles, edges = part.claimedsets()
        return not self.takentiles & tiles and not self.takenedges & edges

    def addpart(self, part):
        self.parts.append(part)
        tiles, edges = part.claimedsets()
        self.takentiles |= tiles
        self.takenedges |= edges
        if part.lightradius > 0:
            self.mask.addp(*part.lightcircle())
            vista.setgrect(self.mask.bounds())
    
    def draw(self):
        for part in self.parts:
            part.draw()

class BodyPart(object):
    lightradius = 0  # How much does this part extend your visibility
    def __init__(self, body, (x,y), edge = 0):
        self.body = body
        self.x, self.y = x, y
        self.worldpos = vista.grid.hextoworld((self.x, self.y))
        self.edge = edge  # Edge number of base
        self.edgeworldpos = vista.grid.edgeworld((self.x, self.y), self.edge)
        self.buds = {}  # New body parts that are formed off this one
                        # (set to None if no body part there yet)

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

class Core(BodyPart):
    """The central core of the body, that has the funny mouth"""
    lightradius = 3
    def __init__(self, body, (x,y) = (0,0)):
        BodyPart.__init__(self, body, (x,y), 0)
        for edge in range(6):  # One bud in each of six directions
            self.buds[vista.grid.opposite((x, y), edge)] = None

    def tiles(self):
        return ((self.x, self.y),)

    def draw(self):
        px, py = vista.worldtoview(vista.grid.hextoworld((self.x, self.y)))
        r = int(vista.grid.a * 0.8)
        pygame.draw.circle(vista.screen, (0, 192, 96), (px, py), r)

class AppendageSpec(object):
    """Data to specify the path of an appendage, irrespective of starting position"""
    def __init__(self, dedges):
        self.dedges = sorted(set(dedges))
    
    def outbuds(self, pos, edge):
        return [vista.grid.opposite(pos, edge + dedge) for dedge in self.dedges]

def randomspec(n = 2):
    return AppendageSpec([random.choice(range(5))+1 for _ in range(n)])


def qBezier((x0,y0), (x1,y1), (x2,y2), n = 12):
    """Quadratic bezier curve"""
    ts = [float(j) / n for j in range(n+1)]
    cs = [((1-t)**2, 2*t*(1-t), t**2) for t in ts]
    return [(a*x0+b*x1+c*x2, a*y0+b*y1+c*y2) for a,b,c in cs]    

class Appendage(BodyPart):
    """A stalk that leads to one or more subsequent buds"""
    def __init__(self, body, (x,y), edge, appspec):
        BodyPart.__init__(self, body, (x,y), edge)
        self.appspec = appspec
        for bud in self.appspec.outbuds((x, y), edge):
            self.buds[bud] = None
        self.color = random.randint(0, 128), random.randint(128, 255), random.randint(0, 128)
    
    def draw(self):
        p0 = self.edgescreenpos()
        p1 = self.screenpos()
        for p, edge in self.buds:
            p2 = self.budscreenpos(p, edge)
            ps = qBezier(p0, p1, p2)
            pygame.draw.lines(vista.screen, self.color, False, ps, 5)
            
class Organ(BodyPart):
    """A functional body part that terminates a stalk"""
    def draw(self):
        p0 = self.screenpos()
#        p1 = vista.grid.gedge((self.x, self.y), self.edge)
#        pygame.draw.line(vista.screen, (0, 192, 64), p0, p1, 5)
        pygame.draw.circle(vista.screen, (0, 192, 64), p0, int(vista.grid.a*0.5))

    def tiles(self):
        return ((self.x, self.y),)

class Eye(Organ):
    """Extends your visible region"""
    lightradius = 3

    def draw(self):
        p0 = self.screenpos()
        p1 = self.edgescreenpos()
        pygame.draw.line(vista.screen, (0, 192, 64), p0, p1, 5)
        pygame.draw.circle(vista.screen, (0, 192, 64), p0, int(vista.grid.a*0.5))
        pygame.draw.circle(vista.screen, (255, 255, 255), p0, int(vista.grid.a*0.4))
        pygame.draw.circle(vista.screen, (0, 0, 0), p0, int(vista.grid.a*0.2))


