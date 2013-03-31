# -*- coding: utf-8 -*-

import pygame, os, cPickle, resource
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
                settings.save()
                savetime = settings.savetimer

        for event in events:
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                if settings.saveonquit:
                    settings.save()
                    game.save()
                pygame.quit()
                return
            if event.type == KEYDOWN and event.key == K_F12:
                vista.screencap()
            if event.type == KEYDOWN and event.key == K_F3:
                settings.showfps = not settings.showfps

        con.think(dt, events, keys, mousepos, buttons)
        con.draw()
        if settings.showfps:
            t = pygame.time.get_ticks() * 0.001
            if int(t / 5.) != int((t - dt) / 5.):  # Update once every 5 seconds
                fpsstring = "%.1ffps" % clock.get_fps()
                try:
                    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
                    fpsstring += " %sMB" % mem
                except:
                    pass
                pygame.display.set_caption("Obb - %s" % fpsstring)
                if settings.fullscreen:
                    print(fpsstring)
        else:
            pygame.display.set_caption("Obb")
        
        

    
