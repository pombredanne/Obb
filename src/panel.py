import pygame
import settings, vista, graphics, mechanics


class Panel(object):
    """Place where available tiles appear and you can pick them"""
    def __init__(self):
        self.tiles = [self.newspec(c) for c in (0,1,2)]
        self.ages = [-2, -2.5, -3]
        self.centers = [(settings.px/2, (j*2+1)*settings.ptilesize) for j in (0,1,2)]
        self.selected = None
        self.trashimg = vista.Surface(80, 80, (64, 64, 64))
        self.trashrect = self.trashimg.get_rect(bottomleft = (20, 440))
        self.cutimg = vista.Surface(80, 80, (128, 0, 0))
        self.cutrect = self.trashimg.get_rect(bottomleft = (100, 440))

    def newspec(self, jtile):
        return mechanics.randomspec("app%s" % jtile)

    def think(self, dt):
        for j in (0,1,2):
            self.ages[j] = min(self.ages[j] + dt, 0)
        
    def draw(self):
        for j, (age, appspec, (cx, cy)) in enumerate(zip(self.ages, self.tiles, self.centers)):
            color = "app%s" % j
            if age < -1: continue
            img = graphics.drawpaneltile(appspec.dedges, color, tilt = age*450)
            rect = img.get_rect(center = (cx, cy))
            vista.psurf.blit(img, rect)
        if self.selected is not None:
            pygame.draw.circle(vista.psurf, (255, 255, 255), self.centers[self.selected], settings.ptilesize, 2)

        vista.psurf.blit(self.trashimg, self.trashrect)
        vista.psurf.blit(self.cutimg, self.cutrect)


    def iconp(self, (mx, my)):
        """Any icons under this position?"""
        mx -= settings.px0
        my -= settings.py0
        for j, (age, (cx, cy)) in enumerate(zip(self.ages, self.centers)):
            if age == 0 and (cx - mx) ** 2 + (cy - my) ** 2 < settings.ptilesize ** 2:
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


