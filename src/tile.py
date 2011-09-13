"""Tile graphics"""

import pygame, math, random
from pygame.locals import *
import vista

def qBezier((x0,y0), (x1,y1), (x2,y2), n = 8):
    """Quadratic bezier curve"""
    ts = [float(j) / n for j in range(n+1)]
    cs = [((1-t)**2, 2*t*(1-t), t**2) for t in ts]
    return [(a*x0+b*x1+c*x2, a*y0+b*y1+c*y2) for a,b,c in cs]    

def mutatecolor((r, g, b)):
    def mutate(x):
        return min(max(x + random.randint(-10, 10), 0), 255)
    return mutate(r), mutate(g), mutate(b)

def drawblobs(surf, color, (x0, y0), (x1, y1), width = None, r0 = None, s0 = 0):
    """A set of random circles within a rectangle going between the two
    specified endpoints. Simulates blobbiness."""
    rstate = random.getstate()
    seed = x0, y0, x1, y1, width, r0, s0
    random.seed(seed)
    dx, dy = x1 - x0, y1 - y0
    d = math.sqrt(dx ** 2 + dy ** 2)
    if width is None: width = d
    if r0 is None: r0 = width / 8
    circs = []
    ncirc = int(4 * width * d / r0 ** 2)
    for j in range(ncirc):
        r = int(random.uniform(r0, 2*r0))
        z = random.uniform(-width/2, width/2)
        q = random.uniform(-width/2, width/2)
        if math.sqrt(z**2 + q**2) + r > width/2: continue
        p = random.uniform(0, d)
        R, G, B = color
        f = 1 - abs(q / width)
        shade = mutatecolor((int(R*f), int(G*f), int(B*f)))
        circs.append((z, p, q, r, shade))
    if random.random() < 0.1:
        while True:  # Add the suction cup
            r = int(2*r0)
            z = random.uniform(-width/2, width/2)
            q = random.uniform(width/3, width/2)
            if math.sqrt(z**2 + q**2) > width/2: continue
            if s0 % 2: q = -q
            p = 0.5 * d
            circs.append((z, p, q, r, (255, 255, 255)))
            break
        
    circs.sort()
        
    for _, p, q, r, shade in circs:
        x = int(x0 + (p * dx + q * dy) / d + 0.5)
        y = int(y0 + (p * dy - q * dx) / d + 0.5)
        pygame.draw.circle(surf, shade, (x, y), r, 0)
    random.setstate(rstate)

def drawapp(dedges, color, zoom, edge0 = 3, cache = {}):
    """Draw appendage"""
    key = tuple(dedges), color, zoom, edge0
    if key in cache:
        return cache[key]
    if zoom == 160:
        img = pygame.Surface((2*zoom, 2*zoom), SRCALPHA)
        def hextooffset((x, y)):
            """Convert hex coordinates to offset within this image"""
            wx, wy = vista.grid.hextoworld((x, y))
            px = int(zoom + zoom * wx + 0.5)
            py = int(zoom - zoom * wy + 0.5)
            return px, py
        p0 = hextooffset(vista.grid.edgehex((0,0), edge0))
        p1 = (zoom, zoom)
        p2s = [hextooffset(vista.grid.edgehex((0,0), edge0 + dedge)) for dedge in dedges]
        pss = [qBezier(p0, p1, p2) for p2 in p2s]
        for j in range(len(pss[0])-1):
            for ps in pss:
                drawblobs(img, color, ps[j], ps[j+1], 0.3*zoom, s0=j)
    else:
        img0 = drawapp(dedges, color, 160, edge0)
        img = pygame.transform.scale(img0, (2*zoom, 2*zoom))
    cache[key] = img
    return img

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 400))

    screen.fill((0, 0, 0))
    drawapp(screen, (1,2,3,4,), (0, 192, 96), (200, 200), 160)
    mini = pygame.transform.smoothscale(screen, (120, 120))
    screen.fill((0, 0, 0))
    screen.blit(mini, mini.get_rect(center = (200, 200)))

    while True:
        if any(event.type in (QUIT, KEYDOWN) for event in pygame.event.get()):
            break
        pygame.display.flip()
    


