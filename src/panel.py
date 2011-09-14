import pygame
import settings, body, vista, graphics


class Panel(object):
    """Place where available tiles appear and you can pick them"""
    def __init__(self):
        self.tiles = [self.newspec(c) for c in (0,1,2)]
        self.ages = [-2, -2.5, -3]
        self.centers = [(settings.px/2, (j*2+1)*settings.ptilesize) for j in (0,1,2)]
        self.selected = None

    def newspec(self, jtile):
        return body.randomspec(2, "app%s" % jtile)

    def think(self, dt):
        for j in (0,1,2):
            self.ages[j] = min(self.ages[j] + dt, 0)
        
    def draw(self):
        for j, (age, appspec, (cx, cy)) in enumerate(zip(self.ages, self.tiles, self.centers)):
            color = "app%s" % j
            if age < -1: continue
            if age == 0:
                img = graphics.tile(appspec.dedges, color)
                rect = img.get_rect(center = (cx, cy))
            else:
                img = graphics.tile(appspec.dedges, color, tilt = age*450)
                rect = img.get_rect(center = (cx+age*300, cy))
            vista.psurf.blit(img, rect)
        if self.selected is not None:
            pygame.draw.circle(vista.psurf, (255, 255, 255), self.centers[self.selected], settings.ptilesize, 2)

    def iconp(self, (mx, my)):
        """Any icons under this position?"""
        mx -= settings.px0
        my -= settings.py0
        for j, (age, (cx, cy)) in enumerate(zip(self.ages, self.centers)):
            if age == 0 and (cx - mx) ** 2 + (cy - my) ** 2 < settings.ptilesize ** 2:
                return j
        return None

    def selecttile(self, jtile = None):
        self.selected = jtile if jtile != self.selected else None

    def claimtile(self, jtile = None):
        if jtile is None: jtile = self.selected
        self.tiles[jtile] = self.newspec(jtile)
        self.ages[jtile] = -6
        self.selected = None


