import pygame, os, cPickle
from pygame.locals import *
import data, vista, context, settings, play, graphics, noise, game


pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=(4096 if settings.audiobuffer else 0))
pygame.init()

def main():
    vista.init()
    vista.addsplash()
    pygame.display.set_caption("Obb is loading.... Please wait")
    noise.nexttrack()
    if settings.restart:
        game.restart()
    else:
        game.load()
    context.push(play.Play())
    clock = pygame.time.Clock()
    savetime = settings.savetimer
    while context.top():
        dt = clock.tick(settings.maxfps) * 0.001 * settings.gamespeed
        dt = min(dt, 1./settings.minfps)
        con = context.top()
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mousepos = pygame.mouse.get_pos()
        buttons = pygame.mouse.get_pressed()

        if settings.autosave:
            savetime -= dt
            if savetime < 0:
                game.save()
                savetime = settings.savetimer

        for event in events:
            if event.type == QUIT:
                if settings.saveonquit:
                    game.save()
                return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                if settings.saveonquit:
                    game.save()
                return
            if event.type == KEYDOWN and event.key == K_F12:
                vista.screencap()
            if event.type == KEYDOWN and event.key == K_F9:  # Manual save
                game.save()
            if event.type == KEYDOWN and event.key == K_F10:  # Debug: change resolution and reload
                game.save()
                settings.sx, settings.sy = 1068, 600
                settings.save()
                settings.load()
                vista.init()

        con.think(dt, events, keys, mousepos, buttons)
        con.draw()
        if settings.showfps:
            pygame.display.set_caption("Obb - %.1ffps" % clock.get_fps())
            if settings.fullscreen:
                print clock.get_fps()
        else:
            pygame.display.set_caption("Obb")
        
        

    
