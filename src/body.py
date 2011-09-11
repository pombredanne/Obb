import pygame, random
import vista

class Body(object):
    def __init__(self, (x, y) = (0, 0)):
        self.core = Core(self, (x, y))
        self.parts = [self.core]
        for _ in range(4):
            p, e = self.core.randombud()
            app = Appendage(self.core, p, e)
            self.core.buds[(p, e)] = app
            self.parts.append(app)
            p, e = app.randombud()
            app2 = Organ(self.core, p, e)
            app.buds[(p, e)] = app2
            self.parts.append(app2)
    
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

    def draw(self):
        px, py = vista.grid.gcenter((self.x, self.y))
        r = int(vista.grid.a * 0.8)
        pygame.draw.circle(vista.screen, (0, 192, 96), (px, py), r)

class Appendage(BodyPart):
    """A stalk that leads to one or more subsequent buds"""
    def __init__(self, body, (x,y), edge):
        BodyPart.__init__(self, body, (x,y), edge)
        for _ in range(2):
            dedge = random.choice(range(5)) + 1
            self.buds[vista.grid.opposite((x, y), edge + dedge)] = None
    
    def draw(self):
        p0 = vista.grid.gcenter((self.x, self.y))
        p1 = vista.grid.gedge((self.x, self.y), self.edge)
        pygame.draw.line(vista.screen, (0, 192, 64), p0, p1, 5)
        for p, edge in self.buds:
            p2 = vista.grid.gedge(p, edge)
            pygame.draw.line(vista.screen, (192, 64, 0), p0, p2, 5)
            
class Organ(BodyPart):
    def draw(self):
        p0 = vista.grid.gcenter((self.x, self.y))
        p1 = vista.grid.gedge((self.x, self.y), self.edge)
        pygame.draw.line(vista.screen, (0, 192, 64), p0, p1, 5)
        pygame.draw.circle(vista.screen, (0, 64, 192), p0, int(vista.grid.a/2))
    

