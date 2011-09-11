import pygame
from pygame.locals import *
import settings

screen = None

def init():
    global screen
    flags = FULLSCREEN if settings.fullscreen else 0
    screen = pygame.display.set_mode(settings.size, flags)

def clear(color = (64, 64, 64)):
    screen.fill(color)

def screencap():
    pygame.image.save(screen, "screenshot.png")


