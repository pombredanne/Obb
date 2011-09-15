import pygame, random
import vista, mechanics


class Twinkler(object):
    """A little bit of energy that can be collected by certain organs"""
    def __init__(self, (x, y)):
        self.x, self.y = x, y
        self.vx = self.vy = 0
        self.t = 0
        self.tugger = None
    
    def think(self, dt):
        self.ax = random.uniform(-8, 8)
        self.ay = random.uniform(-8, 8)
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.t += dt

    def alive(self):
        return self.t < 5

    def draw(self):
        r = int(vista.zoom * 0.3)
        self.img = vista.Surface(r, r, (255, 255, 255))
        pos = vista.worldtoview((self.x, self.y))
        vista.screen.blit(self.img, self.img.get_rect(center = pos))


def newtwinklers(mask, dt):
    ts = []
    dx, dy = mask.x1 - mask.x0, mask.y1 - mask.y0
    N = dx * dy * dt * mechanics.twinklerrate
    for j in range(int(N) + (random.random() < N % 1)):
        x, y = random.uniform(mask.x0, mask.x1), random.uniform(mask.y0, mask.y1)
        ts.append(Twinkler((x, y)))
    return ts    


