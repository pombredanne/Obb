import pygame
from pygame.locals import *

fonts = {}
def img(text = "", size = 32, color = (255, 255, 255), cache = {}):
    key = text, size, color
    if key in cache: return cache[key]
    if size not in fonts:
        fonts[size] = pygame.font.Font(None, size)
    img = fonts[size].render(text, True, color)
    cache[key] = img
    return cache[key]


