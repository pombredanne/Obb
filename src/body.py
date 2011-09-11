import pygame, random
import vista

class Body(object):
    def __init__(self, (x, y) = (0, 0)):
        self.parts = []
        self.takentiles = set()
        self.takenedges = set()
        self.core = Core(self, (x, y))
        self.addpart(self.core)

    def addrandompart(self, n = 1):
        added = 0
        while added < n:
            parent = random.choice(self.parts)
            bud = parent.randombud()
            if not bud: continue
            pos, edge = bud
            if random.random() < 0.5:
                appspec = randomspec()
                part = Appendage(self.core, pos, edge, appspec)
            else:
                part = Organ(self.core, pos, edge)
            if not self.canaddpart(part): continue
            parent.buds[bud] = part
            self.addpart(part)
            added += 1

    def canaddpart(self, part):
        tiles, edges = part.claimedsets()
        return not self.takentiles & tiles and not self.takenedges & edges

    def addpart(self, part):
        self.parts.append(part)
        tiles, edges = part.claimedsets()
        self.takentiles |= tiles
        self.takenedges |= edges
    
    def draw(self):
        for part in self.parts:
            part.draw()

class BodyPart(object):
    def __init__(self, body, (x,y), edge = 0):
        self.body = body
        self.x, self.y = x, y
        self.edge = edge  # Edge number of base
        self.buds = {}  # New body parts that are formed off this one
                        # (set to None if no body part there yet)

    def tiles(self):
        return ()
    
    def edges(self):
        return self.buds.keys()

    def claimedsets(self):
        ts = set(self.tiles())
        es = set(vista.grid.normedge(p, e) for p,e in self.edges())
        return ts, es


    def screenpos(self):
        return vista.grid.gcenter((self.x, self.y))

    def randombud(self):
        """Return a bud that hasn't been used yet"""
        buds = [key for key,value in self.buds.items() if value == None]
        if not buds: return None
        return random.choice(buds)

class Core(BodyPart):
    """The central core of the body, that has the funny mouth"""
    def __init__(self, body, (x,y) = (0,0)):
        BodyPart.__init__(self, body, (x,y), 0)
        for edge in range(6):  # One bud in each of six directions
            self.buds[vista.grid.opposite((x, y), edge)] = None

    def tiles(self):
        return ((self.x, self.y),)

    def draw(self):
        px, py = vista.grid.gcenter((self.x, self.y))
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

class Appendage(BodyPart):
    """A stalk that leads to one or more subsequent buds"""
    def __init__(self, body, (x,y), edge, appspec):
        BodyPart.__init__(self, body, (x,y), edge)
        self.appspec = appspec
        for bud in self.appspec.outbuds((x, y), edge):
            self.buds[bud] = None
    
    def draw(self):
        p0 = vista.grid.gcenter((self.x, self.y))
        p1 = vista.grid.gedge((self.x, self.y), self.edge)
        pygame.draw.line(vista.screen, (0, 192, 64), p0, p1, 5)
        for p, edge in self.buds:
            p2 = vista.grid.gedge(p, edge)
            pygame.draw.line(vista.screen, (192, 64, 0), p0, p2, 5)
            
class Organ(BodyPart):
    """A functional body part that terminates a stalk"""
    def draw(self):
        p0 = vista.grid.gcenter((self.x, self.y))
        p1 = vista.grid.gedge((self.x, self.y), self.edge)
        pygame.draw.line(vista.screen, (0, 192, 64), p0, p1, 5)
        pygame.draw.circle(vista.screen, (0, 64, 192), p0, int(vista.grid.a/2))

    def tiles(self):
        return ((self.x, self.y),)


