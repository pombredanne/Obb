import pygame, random, math
import vista, mechanics, noise, data

baseimg = None
def getimg(zoom, angle, cache = {}):
    global baseimg
    angle = int(angle % 90) / 5 * 5
    zoom  = int(zoom)
    key = zoom, angle
    if key in cache: return cache[key]
    if baseimg is None:
        baseimg = pygame.image.load(data.filepath("twinkler.png")).convert_alpha()
    img = pygame.transform.rotozoom(baseimg, angle, float(zoom) / 240.)
    
    cache[key] = img
    return cache[key]


class Twinkler(object):
    """A little bit of energy that can be collected by certain organs"""
    def __init__(self, (x, y)):
        self.x, self.y = x, y
        self.vx = self.vy = 0
        self.t = 0
        self.sucker = None
        self.claimed = False
    
    def think(self, dt):
        if self.sucker:
            sx, sy = self.sucker.worldpos
            f = math.exp(-dt)
            self.vx *= f
            self.vy *= f
            self.vx += (sx - self.x) * dt
            self.vy += (sy - self.y) * dt
        else:
            self.ax = random.uniform(-4, 4)
            self.ay = random.uniform(-4, 4)
            self.vx += self.ax * dt
            self.vy += self.ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.t += dt
        if self.sucker:
            if (self.x - sx) ** 2 + (self.y - sy) ** 2 < 0.3 ** 2:
                self.claimed = True
                self.sucker.energize()
                self.sucker = None
                noise.play("energize")

    def alive(self):
        return not self.claimed and (self.sucker or self.t < 5)

    def draw(self):
        for r, angle in [(1, self.t * 40), (0.8, self.t * 100), (0.8, self.t * -100)]:
            img = getimg(vista.zoom*r, angle)
            pos = vista.worldtoview((self.x, self.y))
            vista.screen.blit(img, img.get_rect(center = pos))


def newtwinklers(mask, dt):
    ts = []
    dx, dy = mask.x1 - mask.x0, mask.y1 - mask.y0
    N = dx * dy * dt * mechanics.twinklerrate
    for j in range(int(N) + (random.random() < N % 1)):
        x, y = random.uniform(mask.x0, mask.x1), random.uniform(mask.y0, mask.y1)
        ts.append(Twinkler((x, y)))
    return ts    


