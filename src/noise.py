import pygame, os, random, time
import data, font, vista, settings


track = 0
tracks = "ittybitty rocket fighter killing".split()

sounds = {}
plays = {}
def loadsound(name):
    filename = data.filepath(name + ".ogg")
    if os.path.exists(filename):
        sounds[name] = pygame.mixer.Sound(filename)
        sounds[name].set_volume(settings.soundvolume)
        plays[name] = []
    else:
#        print("sound missing: %s" % name)
        sounds[name] = None

def play(name):
    if settings.silent: return

    if name == "removepart": name = "addpart"
    if name == "trash": name = "addpart"
    if name == "addpart":
        return play("addpart-%s" % random.choice((0,1,2)))
    if name not in sounds:
        loadsound(name)
    if sounds[name] is None:
        return
    # Quiet the sound depending on how many times it's played in the last 15 seconds
    # This is because too many shot noises can get kind of annoying
    now = time.time()
    plays[name] = [t for t in plays[name] if t > now - 15]
    v = max(1 - 0.02 * len(plays[name]), 0.3)
    sounds[name].set_volume(v * settings.soundvolume)
    plays[name].append(now)
    sounds[name].play()

def nexttrack():
    global track
    if settings.silent: return
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
    if settings.silent: return
    pygame.mixer.music.pause()

def resume():
    if settings.silent: return
    pygame.mixer.music.unpause()

