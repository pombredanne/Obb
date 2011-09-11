import pygame
from pygame.locals import *
import data, vista, context, settings, play

pygame.init()

def main():
    vista.init()
    pygame.display.set_caption("Ubb")
    context.push(play.Play())
    clock = pygame.time.Clock()
    while context.top():
        dt = min(clock.tick(settings.maxfps) * 0.001, 1./settings.minfps)
        con = context.top()
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mousepos = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed()

        for event in events:
            if event.type == QUIT:
                return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type == KEYDOWN and event.key == K_F12:
                vista.screencap()

        con.think(dt, events, keys, mousepos, buttons)
        con.draw()
        if settings.showfps:
            pygame.display.set_caption("Ubb - %.1ffps" % clock.get_fps())
        pygame.display.flip()
        
        

    
