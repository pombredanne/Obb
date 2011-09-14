"""Graphics module"""

import pygame, math, random
from pygame.locals import *
import vista, settings

colors = {}
colors["app0"] = 0, 1, 0.5, 1
colors["app1"] = 1, 0.5, 0, 1
colors["app2"] = 0.5, 0, 1, 1
colors["target"] = 1, 0, 0, 1


def qBezier((x0,y0), (x1,y1), (x2,y2), n = 8, ccache = {}):
    """Quadratic bezier curve"""
    if n not in ccache:
        ts = [float(j) / n for j in range(n+1)]
        ccache[n] = [((1-t)**2, 2*t*(1-t), t**2) for t in ts]
    return [(a*x0+b*x1+c*x2, a*y0+b*y1+c*y2) for a,b,c in ccache[n]]

def cBezier((x0,y0), (x1,y1), (x2,y2), (x3,y3), n = 8, ccache = {}):
    """Cubic bezier curve"""
    if n not in ccache:
        ts = [float(j) / n for j in range(n+1)]
        ccache[n] = [((1-t)**3, 3*t*(1-t)**2, 3*t**2*(1-t), t**3) for t in ts]
    return [(a*x0+b*x1+c*x2+d*x3, a*y0+b*y1+c*y2+d*y3) for a,b,c,d in ccache[n]]

def drawgraycircles(surf, circs, (x0, y0) = (0, 0)):
    for x, y, r, g in circs:
        pygame.draw.circle(surf, (g,g,g), (x+x0, y+y0), r, 0)

def filtersurface(surf, x, y, z, a=1):
    arr = pygame.surfarray.pixels3d(surf)
    if x != 1: arr[...,0] *= x
    if y != 1: arr[...,1] *= y
    if z != 1: arr[...,2] *= z
    if a != 1: arr[...,3] *= a

def maketransparent(surf):
    filtersurface(surf, 1, 1, 1, 0.5)

def segmentcircles((dx, dy), width = None, r0 = None, s0 = 0, cache = {}):
    """Specs for a bunch of circles in a rectangular pattern between the
    given points"""
    seed = dx, dy, width, r0, s0
    if seed in cache:
        return cache[seed]
    rstate = random.getstate()
    random.seed(seed)
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
        g = int(255 * (1 - abs(q / width)))
        x = int((p * dx + q * dy) / d + 0.5)
        y = int((p * dy - q * dx) / d + 0.5)
        circs.append((z, (x, y, r, g)))
    random.setstate(rstate)
    circs = [circ for z,circ in sorted(circs)]
    cache[seed] = circs
    return circs

def drawgraysegment(surf, (x0, y0), (x1, y1), width = None, r0 = None, s0 = None):
    circs = segmentcircles((x1-x0,y1-y0), width, r0, s0)
    drawgraycircles(surf, circs, (x0,y0))

# Coordinates of vertices and edges
vpos = [(1,0),(.5,-.5),(-.5,-.5),(-1,0),(-.5,.5),(.5,.5)]
epos = [(0,.5),(.75,.25),(.75,-.25),(0,-.5),(-.75,-.25),(-.75,.25)]
s3 = math.sqrt(3)
spos = lambda x,y: (int(settings.tzoom0*(1+x)+.5), int(settings.tzoom0*(1-s3*y)+.5))
vps = [spos(x,y) for x,y in vpos]  # Vertex positions
vips = [spos(.92*x,.92*y) for x,y in vpos]  # inner vertex positions
eps = [spos(x,y) for x,y in epos]

def graystalk(dedge, segs = 8, cache = {}):
    """Image containing a single gray stalk"""
    key = dedge, segs
    if key in cache: return cache[key]
    edge0 = 3
    z = settings.tzoom0
    img = pygame.Surface((2*z,2*z), SRCALPHA)
    p0 = eps[edge0]
    p1 = (z+10,z)
#    p2 = eps[(edge0+dedge)%6]
#    ps = [(int(x+.5),int(y+.5)) for x,y in qBezier(p0, p1, p2, 8)]
    p2 = (z-10,z)
    p3 = eps[(edge0+dedge)%6]
    ps = [(int(x+.5),int(y+.5)) for x,y in cBezier(p0, p1, p2, p3, 8)]
    for j in range(segs):
        drawgraysegment(img, ps[j], ps[j+1], int(z*0.3), None, j)
    cache[key] = img
    return img

def grayapp(dedges, segs = 8, cache = {}):
    """A gray appendage"""
    dedges = tuple(sorted(dedges, key=lambda x:abs(x-3.1)))
    key = dedges, segs
    if key in cache: return cache[key]
    img = graystalk(dedges[0], segs)
    if len(dedges) > 1:
        img = img.copy()
        for dedge in dedges[1:]:
            img.blit(graystalk(dedge, segs), (0,0))
    cache[key] = img
    return cache[key]

def grayapprot(dedges, edge0 = 3, segs = 8, cache = {}):
    """A gray appendange that may be coming in from a different angle"""
    dedges = tuple(sorted(dedges, key=lambda x:abs(x-3.1)))
    key = dedges, edge0, segs
    if key in cache: return cache[key]
    img = grayapp(dedges, segs)
    if edge0 != 3:
        img = pygame.transform.rotate(img, (edge0 - 3) * -60)
    cache[key] = img
    return cache[key]
    
def grayapprotozoom(dedges, edge0 = 3, zoom = None, segs = 8, cache = {}):
    """A gray appendange that may be coming in from a different angle"""
    dedges = tuple(sorted(dedges, key=lambda x:abs(x-3.1)))
    if zoom is None: zoom = settings.tzoom0
    key = dedges, edge0, zoom, segs
    if key in cache: return cache[key]
    img = grayapp(dedges, segs)
    if edge0 != 3 or zoom != settings.tzoom0:
        img = pygame.transform.rotozoom(img, (edge0 - 3) * -60, float(zoom) / settings.tzoom0)
    cache[key] = img
    return cache[key]

def app(dedges, color=(1, 1, 1, 1), edge0 = 3, zoom = settings.tzoom0, segs = 8):
    """A general appendage"""
    img = grayapprotozoom(dedges, edge0, zoom, segs)
    if color in colors: color = colors[color]
    if color not in ((1,1,1), (1,1,1,1)):
        img = img.copy()
        filtersurface(img, color[0], color[1], color[2], color[3])
    return img

heximg = None
def graytile(dedges, cache={}):
    global heximg
    dedges = tuple(sorted(dedges, key=lambda x:abs(x-3.1)))
    if dedges in cache: return cache[dedges]
    if heximg is None:
        heximg = pygame.Surface((2*settings.tzoom0, 2*settings.tzoom0), SRCALPHA)
        pygame.draw.polygon(heximg, (128, 128, 128), vps, 0)
        pygame.draw.polygon(heximg, (64, 64, 64), vips, 0)
    img = heximg.copy()
    appimg = grayapp(dedges)
    img.blit(appimg, (0, 0))
    cache[dedges] = img
    return img

def graytilerotozoom(dedges, zoom = settings.ptilesize, tilt = 0, cache = {}):
    tilt = int(tilt / 10 + 0.5) * 10 % 360
    dedges = tuple(sorted(dedges, key=lambda x:abs(x-3.1)))
    key = dedges, zoom, tilt
    if key in cache: return cache[key]
    img = graytile(dedges)
    if tilt != 0 or zoom != settings.tzoom0:
        img = pygame.transform.rotozoom(img, -tilt, float(zoom) / settings.tzoom0)
    cache[key] = img
    return cache[key]

def tile(dedges, color=(1, 1, 1, 1), zoom = settings.ptilesize, tilt = 0):
    """Draw one of the placeable tiles that appears in the side panel"""
    img = graytilerotozoom(dedges, zoom, tilt)
    if color in colors: color = colors[color]
    if color not in ((1,1,1), (1,1,1,1)):
        img = img.copy()
        filtersurface(img, color[0], color[1], color[2], color[3])
    return img

dedgesets = [(1,), (2,), (3,), (4,), (5,), (1,2), (1,3), (1,4), (1,5),
    (2,3), (2,4), (2,5), (3,4), (3,5), (4,5)]

def loadallappimages(zooms = None):
    if zooms is None:
        for dedges in dedgesets:
            for segs in (1,2,3,4,5,6,7,8):
                grayapp(dedges, segs)
    else:
        for dedges in dedgesets:
            for edge0 in range(6):
                for segs in (1,2,3,4,5,6,7,8):
                    for zoom in zooms:
                        grayapprotozoom(dedges, edge0, zoom, segs)
    return None


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 400))

    screen.fill((0, 0, 0))
    img = pygame.Surface((200, 200), SRCALPHA)

    t0 = pygame.time.get_ticks()
    loadallappimages([60])
    t1 = pygame.time.get_ticks()
    print t1 - t0

    
    if False:
        circs = [(random.uniform(-100, 100), random.uniform(-100, 100), random.uniform(5, 20), random.uniform(64, 192)) for _ in range(2000)]
        circs = [(int(x),int(y),int(r),c) for x,y,r,c in circs if x**2 + y**2 < 100**2]

        for _ in range(10):
            img.fill((0,0,0))
            t0 = pygame.time.get_ticks()
            drawgraycircles(img, circs, (100, 100))
            s = pygame.surfarray.pixels3d(img)
            s[...,0] *= 1
            s[...,1] *= 0.6
            s[...,2] *= 0
            del s
            t1 = pygame.time.get_ticks()
            print t1 - t0
    if False:
        for _ in range(10):
            img.fill((0,0,0))
            t0 = pygame.time.get_ticks()
            drawgraysegment(img, (100, 50), (100, 150))
            filtersurface(img, 1, 0.6, 0)
            t1 = pygame.time.get_ticks()
            print t1 - t0
    if True:
        for _ in range(10):
            t0 = pygame.time.get_ticks()
            img = app((1,2,3), (1, 0.8, 0), 1, 60)
            filtersurface(img, 1, 1, 0)
            t1 = pygame.time.get_ticks()
            print t1 - t0
        
    t0 = pygame.time.get_ticks()
    screen.blit(img, (0,0))
    t1 = pygame.time.get_ticks()
    print t1 - t0
    

    while True:
        if any(event.type in (QUIT, KEYDOWN) for event in pygame.event.get()):
            break
        pygame.display.flip()


