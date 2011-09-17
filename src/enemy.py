import pygame, random, math
import vista, mechanics, noise, data, settings, twinkler


def getimg(name, cache = {}):
    if name in cache: return cache[name]
    cache[name] = pygame.image.load(data.filepath(name + ".png")).convert_alpha()
    return cache[name]

def getshotimg(zoom, angle = 0, cache = {}):
    angle = int(angle % 90) / 5 * 5
    zoom  = int(zoom)
    key = zoom, angle
    if key in cache: return cache[key]
    cache[key] = pygame.transform.rotozoom(getimg("shot"), angle, float(zoom) / 240.)
    return cache[key]

spoils = []  # Twinklers that get created when you kill an enemy

class Shot(object):
    """A projectile. No not that kind. Wait, actually, yes, that kind."""
    v0 = 3
    dhp = 1
    hp0 = 1
    ntwinklers = 1
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
        self.hp = self.hp0
        self.angle = 0
        self.omega = random.uniform(30, 120) * (1 if random.random() < 0.5 else -1)

    def think(self, dt):
        self.t -= dt
        self.angle += self.omega * dt
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
        if self.t <= 0 and self.active:
            self.active = False
            self.complete()


    def complete(self):
        self.target.hit(self.dhp)

    def hit(self, dhp = 1):
        self.hp -= dhp
        if self.hp <= 0:
            self.active = False
            for _ in range(self.ntwinklers):
                spoils.append(twinkler.Twinkler((self.x, self.y)))

    def alive(self):
        return self.active and self.t > 0

    def draw(self):
        pos = vista.worldtoview((self.x, self.y))
        img = getshotimg(vista.zoom, self.angle)
        vista.screen.blit(img, img.get_rect(center = pos))

class Ship(Shot):
    """A shot that spawns more shots. Yikes!"""


def newshots(body):
    shots = []
    mx0, my0, mx1, my1 = body.mask.bounds()
    for part in body.parts:
        if not part.targetable: continue
        wx, wy = part.worldpos
        p = 1 - math.exp(-(wx ** 2 + wy ** 2) / 2000)
        if settings.barrage:
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



