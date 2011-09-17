import pygame
import data


track = 0
tracks = ["fighter", "ittybitty"]

def play(name = ""):
    pass

def nexttrack():
    global track
    if track == len(tracks):  # music off
        pygame.mixer.music.stop()
        track = 0
    else:
        fname = data.filepath(tracks[track] + ".ogg")
        pygame.mixer.music.load(fname)
        pygame.mixer.music.play(-1)
        track += 1

def pause():
    pass

def resume():
    pass

