import pygame
from pygame.locals import *
import data, settings

fonts = {}
def img(text = "", size = 32, color = (255, 255, 255), cache = {}):
    key = text, size, color
    if key in cache: return cache[key]
    if size not in fonts:
        fonts[size] = pygame.font.Font(data.filepath("suckgolf.ttf"), size)
    img = fonts[size].render(text.replace("0", "o"), True, color)
    if img.get_width() > settings.maxtextwidth:
        img = pygame.transform.smoothscale(img, (settings.maxtextwidth, img.get_height()))
    cache[key] = img
    return cache[key]

def blocktext(text = "", size = 32, color = (255, 255, 255), cache = {}):
    key = text, size, color
    if key in cache: return cache[key]
    if size not in fonts:
        fonts[size] = pygame.font.Font(data.filepath("suckgolf.ttf"), size)
    img = fonts[size].render(text.replace("0", "o"), True, color)
    cache[key] = img
    return cache[key]



