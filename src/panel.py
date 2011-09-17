import pygame
import settings, vista, graphics, mechanics, font


class Panel(object):
    """Place where available tiles appear and you can pick them"""
    def __init__(self, body):
        self.body = body
        self.tiles = [self.newspec(c) for c in (0,1,2)]
        self.ages = [-2, -2.5, -3]
        ys = [(j*1.9+1)*settings.layout.ptilesize + settings.layout.ptiley for j in (0,1,2)]
        self.centers = [(settings.px/2, int(y)) for y in ys]
        self.selected = None
        self.loadrate = mechanics.baseloadrate
        self.cubeimg = graphics.cube.img(zoom = settings.layout.organcountsize, edge0 = 0)
        self.cuberect = self.cubeimg.get_rect(center = settings.layout.cubeiconpos)

    def newspec(self, jtile):
        return mechanics.randomspec("app%s" % jtile)

    def think(self, dt):
        self.loadrate = mechanics.baseloadrate + mechanics.cubeloadrate * self.body.ncubes
        for j in (0,1,2):
            self.ages[j] = min(self.ages[j] + (1 if self.ages[j] > -1 else self.loadrate) * dt, 0)
        
    def draw(self):
        for j, (age, appspec, (cx, cy)) in enumerate(zip(self.ages, self.tiles, self.centers)):
            color = "app%s" % j
            if age < -1:
                img = graphics.loadbar(1 - ((-age-1) / 5), color)
                rect = img.get_rect(center = (cx, cy))
            else:
                img = graphics.drawpaneltile(appspec.dedges, color, tilt = age*450)
                rect = img.get_rect(center = (cx + age*300, cy))
            vista.psurf.blit(img, rect)
        if self.selected is not None:
            pygame.draw.circle(vista.psurf, (255, 255, 255), self.centers[self.selected], settings.layout.ptilesize, 2)

        # Draw cube tally
        color, size = (0,0,0), settings.layout.countsize
        img = font.img("%s" % (self.body.ncubes), size=size, color=color)
        vista.psurf.blit(self.cubeimg, self.cuberect)
        vista.psurf.blit(img, img.get_rect(midleft = self.cuberect.midright))


    def iconp(self, (mx, my)):
        """Any icons under this position?"""
        mx -= settings.px0
        my -= settings.py0
        for j, (age, (cx, cy)) in enumerate(zip(self.ages, self.centers)):
            if age == 0 and (cx - mx) ** 2 + (cy - my) ** 2 < settings.layout.ptilesize ** 2:
                return j
        return None

    def trashp(self, (mx, my)):
        mx -= settings.px0
        my -= settings.py0
        return self.trashrect.collidepoint((mx, my))

    def cutp(self, (mx, my)):
        mx -= settings.px0
        my -= settings.py0
        return self.cutrect.collidepoint((mx, my))

    def selecttile(self, jtile = None):
        self.selected = jtile if jtile != self.selected else None

    def claimtile(self, jtile = None):
        if jtile is None: jtile = self.selected
        self.tiles[jtile] = self.newspec(jtile)
        self.ages[jtile] = -6
        self.selected = None


