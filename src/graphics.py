"""Graphics module"""

import pygame, math, random
from pygame.locals import *
import vista, settings, mechanics

colors = {}
colors["app0"] = 0, 0.8, 0.4, 1
colors["app1"] = 0.8, 0.4, 0, 1
colors["app2"] = 0.7, 0, 1, 1
colors["target"] = 1, 0, 0, 1
colors["core"] = 0.2, 1, 0.2, 1
colors["ghost"] = 1, 1, 1, 0.4
colors["badghost"] = 1, 0, 0, 0.4


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
    for _, x, y, r, g in circs:
        pygame.draw.circle(surf, (g,g,g), (x+x0, y+y0), r, 0)

def drawchannelcircles(surf, allcircs, (x0, y0) = (0, 0)):
    assert len(allcircs) <= 3
    circs = [(z,x,y,r,(g,0,0)) for z,x,y,r,g in allcircs[0]]
    if len(allcircs) > 1: circs += [(z,x,y,r,(0,g,0)) for z,x,y,r,g in allcircs[1]]
    if len(allcircs) > 2: circs += [(z,x,y,r,(0,0,g)) for z,x,y,r,g in allcircs[2]]
    for _, x, y, r, color in sorted(circs):
        pygame.draw.circle(surf, color, (x+x0, y+y0), r, 0)

# This function is idempotent. Just in case anyone asks.
def normcircles(circs):
    circs[:] = [(z, int(x+.5), int(y+.5), int(r+.5), min(max(int(g+.5),0),255))
                for z,x,y,r,g in sorted(circs)]

def filtersurface(surf, x, y, z, a=1):
    arr = pygame.surfarray.pixels3d(surf)
    if x != 1: arr[...,0] *= x
    if y != 1: arr[...,1] *= y
    if z != 1: arr[...,2] *= z
    if a != 1: pygame.surfarray.pixels_alpha(surf)[:] *= a

def maketransparent(surf):
    filtersurface(surf, 1, 1, 1, 0.5)

class Circles(object):
    """A graphic that's made from repeated calls to pygame.draw.circles"""
    def __init__(self):
        self.cache = {}
        self.imgcache = {}

    def setdefaults(self, *args):
        """Return a list that's in the same order as the args to getkey
        and getcircles"""
        return args

    def getkey(self, *args):
        return tuple(args)

    def getcircles(self):
        """Be a generator, make things easier"""
        raise NotImplementedError

    def __call__(self, *args, **kw):
        args = self.setdefaults(*args, **kw)
        key = self.getkey(*args)
        if key in self.cache: return self.cache[key]
        rstate = random.getstate()
        random.seed(key)
        circs = list(self.getcircles(*args))
        normcircles(circs)
        random.setstate(rstate)
        self.cache[key] = circs
        return circs

    def draw(self, surf, offset, *args, **kw):
        circs = self(*args, **kw)
        drawgraycircles(surf, circs, offset)

    def grayimg(self, size, *args, **kw):
        size = int(size)
        key = self.getimgkey(size, *args, **kw)
        if key in self.imgcache: return self.imgcache[key]
        img = vista.Surface(2*size)
        self.issuedraw(img, *key)
        self.imgcache[key] = img
        return img

    def graytile(self, zoom = settings.tzoom0, *args, **kw):
        key = zoom, self.getimgkey(*args, **kw)
        if key in self.imgcache: return self.imgcache[key]
        if zoom == settings.tzoom0:
            img0 = self.grayimg(*args, **kw)
            img = vista.Surface(2*zoom)
            img.blit(img0, img0.get_rect(center = (zoom,zoom)))
        else:
            img0 = self.graytile(settings.tzoom0, *args, **kw)
            img = pygame.transform.smoothscale(img0, (2*zoom, 2*zoom))
        self.imgcache[key] = img
        return img


class SegmentCircles(Circles):
    def setdefaults(self, (dx, dy), width = None, r0 = None, s0 = 0):
        d = math.sqrt(dx ** 2 + dy ** 2)
        if width is None: width = d
        if r0 is None: r0 = width / 8
        return (dx, dy), d, width, r0, s0

    def getcircles(self, (dx, dy), d, width, r0, s0):
        ncirc = int(4 * width * d / r0 ** 2)
        for j in range(ncirc):
            r = random.uniform(r0, 2*r0)
            z = random.uniform(-width/2, width/2)
            q = random.uniform(-width/2, width/2)
            if math.sqrt(z**2 + q**2) + r > width/2: continue
            p = random.uniform(0, d)
            g = 255 * (1 - abs(q / width))
            x = (p * dx + q * dy) / d
            y = (p * dy - q * dx) / d
            yield z, x, y, r, g


segmentcircles = SegmentCircles()

class SphereCircles(Circles):
    def setdefaults(self, R, r0 = None, lvector = (-1,-1,2)):
        if r0 is None: r0 = R / 10.
        return R, r0, tuple(lvector)

    def getcircles(self, R, r0, (lx, ly, lz)):
        sl = math.sqrt(lx ** 2 + ly ** 2 + lz ** 2)
        ncirc = int(40 * R ** 2 / r0 ** 2)
        for j in range(ncirc):
            r = random.uniform(r0, 2*r0)
            x = random.uniform(-R, R)
            y = random.uniform(-R, R)
            z = random.uniform(-R, R)
            if math.sqrt(x ** 2 + y ** 2 + z ** 2) + r > R: continue
            g = 255 * (0.55 + 0.45 * (lx*x+ly*y+lz*z)/sl/R)
            yield z, x, y, r, g

    def getimgkey(self, size, r0 = None):
        return size, r0

    def issuedraw(self, img, size, r0):
        self.draw(img, (size, size), size, r0)


spherecircles = SphereCircles()

class LobeCircles(SphereCircles):
    def setdefaults(self, R, angle = 0, r0 = None, lvector = (-1,-1,2)):
        if r0 is None: r0 = R / 10.
        return R, angle, r0, tuple(lvector)

    def getcircles(self, R, angle, r0, lvector):
        C, S = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        for z, x, y, r, g in SphereCircles.getcircles(self, R, r0, lvector):
            if abs(x) < 0.95*r: continue
            if math.sqrt((1.2*x) ** 2 + y ** 2 + z ** 2) + r > R: continue
            x, y = C * x - S * y, C * y + S * x
            yield z, x, y, r, g

    def getimgkey(self, size, angle = 0, r0 = None):
        return size, angle, r0

    def issuedraw(self, img, size, angle, r0):
        self.draw(img, (size, size), size, angle, r0)


lobecircles = LobeCircles()

class HelixCircles(Circles):
    def setdefaults(self, (dx, dy), offs = None, R = None, r = None, coil = None):
        if offs is None: offs = (0, 0.4)
        offs = tuple(sorted(offs))
        if R is None: R = 16
        if r is None: r = int(R / 3)
        if coil is None: coil = R*6
        return (dx, dy), offs, R, r, coil

    def getcircles(self, (dx, dy), offs, R, r, coil):
        d = math.sqrt(dx ** 2 + dy ** 2)
        nextrung = r
        for j in range(int(2. * d / r)):
            h = j / (2. / r)
            angles = [(h / coil + off) * 2 * math.pi for off in offs]
            Ss = [math.sin(angle) for angle in angles]
            Cs = [math.cos(angle) for angle in angles]
            xs = [int(R * S * dy / d + h * dx / d + 0.5) for S in Ss]
            ys = [int(-R * S * dx / d + h * dy / d + 0.5) for S in Ss]
            gs = [int(255 * (0.8 + 0.2 * C)) for C in Cs]
            zs = Cs
            for z,x,y,g in zip(zs, xs, ys, gs):
                yield z, x, y, r, g
            if len(offs) == 2 and h > nextrung:
                nextrung += 1.7 * r
                (x0, x1), (y0, y1), (g0, g1), (z0, z1) = xs, ys, gs, zs
                for k in range(20):
                    k *= 0.05
                    x = int(x0 + k * (x1 - x0))
                    y = int(y0 + k * (y1 - y0))
                    z = z0 + k * (z1 - z0)
                    g = int(g0 + k * (g1 - g0))
                    yield z, x, y, r*.6, g

helixcircles = HelixCircles()




def sphere(Rfac, color=(1, 1, 1, 1), zoom = settings.tzoom0):
    R = int(Rfac * settings.tzoom0)
    img = spherecircles.graytile(zoom, R)
    if color in colors: color = colors[color]
    if color not in ((1,1,1), (1,1,1,1)):
        img = img.copy()
        filtersurface(img, color[0], color[1], color[2], color[3])
    return img

def lobes(Rfac, color=(1, 1, 1, 1), angle = 0, zoom = settings.tzoom0):
    R = int(Rfac * settings.tzoom0)
    img = lobecircles.graytile(zoom, R, angle)
    if color in colors: color = colors[color]
    if color not in ((1,1,1), (1,1,1,1)):
        img = img.copy()
        filtersurface(img, color[0], color[1], color[2], color[3])
    return img

def organ(Rfac, color=(1,1,1,1), edge0=3, zoom = settings.tzoom0, segs = 3):
    """A sphere on a stalk"""
    img = app((3,), color, edge0, zoom, segs=segs).copy()
    if Rfac:
        sphereimg = sphere(Rfac, color, (0,0), zoom)
        img.blit(sphereimg, sphereimg.get_rect(center = img.get_rect().center))
    return img

def brain(Rfac = 0.6, color=None, edge0=3, zoom = settings.tzoom0, segs = 3):
    img = app((3,), color or colors["app0"], edge0, zoom, segs=segs).copy()
    if Rfac:
        lobeimg = lobes(Rfac, color or (1,.8,.8,1), (edge0%3)*60, zoom)
        img.blit(lobeimg, lobeimg.get_rect(center = img.get_rect().center))
    return img

# TODO: support transparency in eyeballs
def eyeball(blink = 1, edge0 = 3, zoom = settings.tzoom0, cache = {}):
    blink = int(blink * 6) / 6.
    edge0 = 0 if blink == 1 else edge0 % 3
    key = zoom, edge0, blink
    if key in cache: return cache[key]
    if zoom == settings.tzoom0 and edge0 == 0:
        img = vista.Surface(2*zoom)
        if blink == 1:
            pygame.draw.circle(img, (255, 255, 255), (zoom, zoom), int(zoom * 0.35))
        else:
            rect = pygame.Rect(0, 0, int(zoom * 0.7), int(zoom * 0.7 * blink))
            rect.center = zoom, zoom
            pygame.draw.ellipse(img, (255, 255, 255), rect)
        if blink >= 0.5:
            pygame.draw.circle(img, (0, 0, 0), (zoom, zoom), int(zoom * 0.16))
    else:
        img0 = eyeball(blink)
        img = pygame.transform.rotozoom(img0, -60 * edge0, float(zoom) / settings.tzoom0)
    cache[key] = img
    return cache[key]

def eye(color=(1,1,1,1), edge0=3, blink = 1, zoom = settings.tzoom0):
    """An organ with some circles on it"""
    img = organ(0.5, color, edge0, zoom)
    eyeimg = eyeball(blink, edge0, zoom)
    img.blit(eyeimg, eyeimg.get_rect(center = img.get_rect().center))
    return img

# TODO: implement blinkage
def eyebrain(Rfac = 0.6, color=None, edge0=3, blink = 1, zoom = settings.tzoom0, segs = 3):
    img = app((3,), color or colors["app0"], edge0, zoom, segs=segs).copy()
    if Rfac:
        lobeimg = lobes(Rfac, color or (1,.8,.8,1), (edge0%3)*60, zoom)
        img.blit(lobeimg, lobeimg.get_rect(center = img.get_rect().center))
        x0, y0 = img.get_rect().center
        for dedge,r in ((0,0.3),(1,0.4),(2,0.1),(2,0.45),(3,0.35),(4,0.4),(5,.25)):
            angle = math.radians((edge0 + dedge) * 60 + 20)
            dx = int(zoom * r * math.sin(angle) * Rfac / 0.6)
            dy = -int(zoom * r * math.cos(angle) * Rfac / 0.6)
            eyeimg = eyeball(1-r/2, (dedge+edge0)%6, int(zoom/2.5))
            img.blit(eyeimg, eyeimg.get_rect(center = (x0+dx,y0+dy)))
    return img


stalkimages = []
def core(_color, growth = 0, zoom = settings.tzoom0):
    z = settings.tzoom0
    img = vista.Surface(3*z)
    if not stalkimages:
        for edge in range(6):
            stalkimg = vista.Surface(z)
            x0, y0 = stalkimg.get_rect().center
            stalkimg.fill((0,0,0,0))
            r, g, b, a = colors["app%s" % (edge % 3)]
            S, C = math.sin(math.radians(60 * edge)), -math.cos(math.radians(60 * edge))
            dx, dy = 0.3 * S * z, 0.3 * C * z
            segmentcircles.draw(stalkimg, (x0,y0), (dx, dy), 0.3 * z)
            filtersurface(stalkimg, r, g, b, a)
            stalkimages.append(stalkimg)
    for edge in range(6):
        stalkimg = stalkimages[edge]
        x0, y0 = stalkimg.get_rect().center
        S, C = math.sin(math.radians(60 * edge)), -math.cos(math.radians(60 * edge))
        dx, dy = 0.3 * S * z, 0.3 * C * z
        dr = min(max((1 - growth) * 4 - 0.2 * (5 - edge), 0), 0.5) if growth != 1 else 0
        x, y = (1.5+(.65-dr)*S) * z, (1.5+(.65-dr)*C) * z
        img.blit(stalkimg, stalkimg.get_rect(center = (x,y)))
    sphereimg = sphere(0.75, _color, zoom = z)
    img.blit(sphereimg, sphereimg.get_rect(center = img.get_rect().center))
    return pygame.transform.smoothscale(img, (3*zoom, 3*zoom))


# Coordinates of vertices and edges
vpos = [(1,0),(.5,-.5),(-.5,-.5),(-1,0),(-.5,.5),(.5,.5)]
epos = [(0,.5),(.75,.25),(.75,-.25),(0,-.5),(-.75,-.25),(-.75,.25)]
s3 = math.sqrt(3)
spos = lambda x,y: (int(settings.tzoom0*(1+x)+.5), int(settings.tzoom0*(1-y)+.5))
vps = [spos(x,s3*y) for x,y in vpos]  # Vertex positions
vips = [spos(.92*x,.92*s3*y) for x,y in vpos]  # inner vertex positions
eps = [spos(x,s3*y) for x,y in epos]
if settings.twisty:
    angles = [math.radians(60*a+10) for a in range(6)]
    eips = [spos(.5*math.sin(a),.5*math.cos(a)) for a in angles]
else:
    eips = [spos(0,0) for a in range(6)]

def graystalk(dedge, segs = 8, cache = {}):
    """Image containing a single gray stalk"""
    key = dedge, segs
    if key in cache: return cache[key]
    edge0 = 3
    z = settings.tzoom0
    img = vista.Surface(2*z)
    p0 = eps[edge0]
    p1 = eips[edge0]
    p2 = eips[(edge0+dedge)%6]
    p3 = eps[(edge0+dedge)%6]
    ps = cBezier(p0, p1, p2, p3, 8)
    ps = [(int(x+.5),int(y+.5)) for x,y in ps]
    for j in range(segs):
        (x0, y0), (x1, y1) = ps[j], ps[j+1]
        segmentcircles.draw(img, (x0,y0), (x1-x0,y1-y0), z*0.3, None, j)
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
        heximg = vista.Surface(2*settings.tzoom0)
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

def loadallappimages(zooms = None):
    if zooms is None:
        for dedges in mechanics.dedgesets:
            for segs in (1,2,3,4,5,6,7,8):
                grayapp(dedges, segs)
    else:
        for dedges in mechanics.dedgesets:
            for edge0 in range(6):
                for segs in (1,2,3,4,5,6,7,8):
                    for zoom in zooms:
                        grayapprotozoom(dedges, edge0, zoom, segs)
    return None

def meter(img, level, color1 = (0.5, 0, 1), color0 = (0.2, 0.2, 0.2)):
    img2 = img.copy()
    h = img2.get_height()
    p = h - level
    arr = pygame.surfarray.pixels3d(img2)
    x, y, z = color1
    if x != 1: arr[...,p:,0] *= x
    if y != 1: arr[...,p:,1] *= y
    if z != 1: arr[...,p:,2] *= z
    x, y, z = color0
    if x != 1: arr[...,:p,0] *= x
    if y != 1: arr[...,:p,1] *= y
    if z != 1: arr[...,:p,2] *= z
    return img2

def icon(name):
    s = settings.largeiconsize
    img = vista.Surface(s)
    if name in ("eye", "brain", "eyebrain"):
        r, g, b, a = colors["app0"]
    color0 = int(r*255), int(g*255), int(b*255)
    color1 = int(r*128), int(g*128), int(b*128)
    img.fill(color0)
    img.fill(color1, (3, 3, s-6, s-6))
    return img

def ghostify(img):
    img2 = img.copy()
    arr = pygame.surfarray.pixels3d(img2)
    g = (arr[...,0] + arr[...,1] + arr[...,2]) / 6
    arr[...,0] = arr[...,1] = arr[...,2] = g
    return img2
    


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 400))

    screen.fill((0, 0, 0))
    img = vista.Surface(200)

    if False:
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
    if False:
        for _ in range(10):
            t0 = pygame.time.get_ticks()
            img = app((1,2,3), (1, 0.8, 0), 1, 60)
            filtersurface(img, 1, 1, 0)
            t1 = pygame.time.get_ticks()
            print t1 - t0
    if False:
        img = sphere(0.5, color = "ghost", zoom = 60)
    if True:
#        drawgraylobes(img, (100, 100), 60, 10)
#        img = sphere(0.5, color = "ghost", zoom = 60)
        img = brain()
        img = brain(edge0=1)
    if False:
        img = vista.Surface(40, 400, (0, 0, 0))
        drawgrayhelix(img, (20,0), (20,400))
        img = meter(img, 100)
        
    t0 = pygame.time.get_ticks()
    screen.blit(img, (0,0))
    t1 = pygame.time.get_ticks()
    print t1 - t0
    

    while True:
        if any(event.type in (QUIT, KEYDOWN) for event in pygame.event.get()):
            break
        pygame.display.flip()


