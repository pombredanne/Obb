import pygame, os, random
import data, font, vista, settings


track = 0
tracks = ["rocket", "fighter", "ittybitty", "killing"]

sounds = {}
def play(name = ""):
    if name == "addpart":
        return play("addpart-%s" % random.choice((0,1,2)))
    if name not in sounds:
        filename = data.filepath(name + ".ogg")
        if os.path.exists(filename):
            sounds[name] = pygame.mixer.Sound(filename)
        else:
            print "sound missing: %s" % name
            sounds[name] = None
    if sounds[name] is not None:
        sounds[name].play()
        
    

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
    vista.musicicontext = font.img(str(track), size = settings.layout.countsize, color=(0,0,0))

def pause():
    pygame.mixer.music.pause()

def resume():
    pygame.mixer.music.unpause()

