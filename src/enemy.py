import pygame, random, math
import vista, mechanics, noise


class Shot(object):
    """A projectile. No not that kind. Wait, actually, yes, that kind."""
    v0 = 3
    def __init__(self, (x, y), target):
        self.x, self.y = x, y
        self.target = target
        self.tx, self.ty = self.target.worldpos
        self.dx, self.dy = x - self.tx, y - self.ty
        d = math.sqrt(self.dx ** 2 + self.dy ** 2)
        self.t = d / self.v0
        self.dx /= self.t
        self.dy /= self.t
        self.passedshields = []
        self.active = True

    def think(self, dt):
        self.t -= dt
        self.x = self.tx + self.t * self.dx
        self.y = self.ty + self.t * self.dy
        for shield in self.target.body.shields:
            if shield in self.passedshields:
                continue
            sx, sy = shield.worldpos
            if (sx - self.x) ** 2 + (sy - self.y) ** 2 < shield.shield ** 2:
                if random.random() < 0.5:
                    self.passedshields.append(shield)
                    shield.wobble()
                else:
                    self.active = False
                    noise.play("dink")
            

    def alive(self):
        return self.active and self.t > 0

    def draw(self):
        r = int(vista.zoom * 0.2)
        self.img = vista.Surface(r, r, (255, 0, 0))
        pos = vista.worldtoview((self.x, self.y))
        vista.screen.blit(self.img, self.img.get_rect(center = pos))

def newshots(body):
    shots = []
    mx0, my0, mx1, my1 = body.mask.bounds()
    for part in body.parts:
        if not part.targetable: continue
        wx, wy = part.worldpos
#        p = 1 - math.exp(-(wx ** 2 + wy ** 2) / 2000)
        p = 0.5
        if random.random() > p: continue

        x = wx * random.uniform(0.5, 1.5)
        y = wy * random.uniform(0.5, 1.5)
        while mx0 < x < mx1 and my0 < y < my1:
            x *= 1.3
            y *= 1.3
            x += random.uniform(-1, 1)
            y += random.uniform(-1, 1)
        shots.append(Shot((x, y), part))
    return shots



