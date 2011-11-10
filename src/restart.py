import pygame
import context, game, font, graphics, vista, settings

class Restart(context.Context):
    def __init__(self):
        self.background = graphics.ghostify(vista._screen.convert_alpha())
        self.cloudticker = 0
        self.active = True
        text = "Press y to delete your saved game and start over, or any other key to return to the game"
        self.textimg = font.blocktext(text, size = settings.layout.tipsize)
        self.torestart = False

    def think(self, dt, events, keys, mousepos, buttons):
        if self.active:
            self.cloudticker = min(self.cloudticker + dt, 0.25)
        else:
            self.cloudticker = max(self.cloudticker - dt, 0)
            if not self.cloudticker:
                context.pop()
                if self.torestart:
                    game.restart()

        if self.cloudticker == 0.25 and self.active:
            for event in events:
                if event.type == pygame.KEYUP:
                    self.active = False
                    self.torestart = event.key == pygame.K_y

    def draw(self):
        vista._screen.blit(self.background, (0,0))
        width, height = self.textimg.get_size()
        bubble = graphics.thoughtbubble(height, width, f = self.cloudticker*4)
        bubblerect = bubble.get_rect(center = (settings.sx/2, settings.sy/2))
        vista._screen.blit(bubble, bubblerect)
        if self.cloudticker == 0.25:
            rect = self.textimg.get_rect(center = vista._screen.get_rect().center)
            vista._screen.blit(self.textimg, rect)
        pygame.display.flip()
        
        
