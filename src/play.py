import pygame, random
import vista, context, body, settings

class Play(context.Context):
    def __init__(self):
        self.body = body.Body()
        
        px, py = self.body.core.screenpos()
        ps = [((px/10, py/10), 20)]
        for part in self.body.parts:
            if isinstance(part, body.Organ):
                px, py = part.screenpos()
                ps.append(((px/10, py/10), 20))
        self.mask = vista.Mask((settings.sx/10, settings.sy/10), ps)
        self.mask = pygame.transform.smoothscale(self.mask.surf, settings.size)

    def think(self, dt, events, keys, mousepos, buttons):
        self.ton = vista.grid.tnearest(mousepos)

    def draw(self):
        vista.clear((0,0,0))
#        for _ in range(2000):
#            x = random.randint(0,settings.sx)
#            y = random.randint(0,settings.sy)
#            vista.screen.set_at((x,y), (255, 255, 255))
        for x in range(-6, 6):
            for y in range(-6, 6):
                vista.grid.drawhex((x,y))
#        vista.clear()
        vista.grid.drawhex(self.ton, (255, 255, 255))
        self.body.draw()
        vista.screen.blit(self.mask, (0,0))

