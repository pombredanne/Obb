# Obb map creator
# Run this from your root Obb directory:

#    python make-obb-map.py [-z zoomfactor] [-o outputfile.png] [--showhexes]

# The zoom factor defaults to 72, which is all the way zoomed in in the
#   game. The output file defaults to obb-map.png. Enjoy!

import sys, os, cPickle, pygame, random
from src import data, vista, settings

zoom = 72
mapfile = "obb-map.png"
showhexes = "--showhexes" in sys.argv

for j in range(len(sys.argv)):
    if sys.argv[j] == "-z":
        zoom = int(sys.argv[j+1])
    elif sys.argv[j] == "-o":
        mapfile = sys.argv[j+1]


savefile = data.filepath("savegame.pkl")
play = cPickle.load(open(savefile, "rb"))

pygame.init()
vista.init()
pygame.display.set_caption("Preparing to make make map. Please wait....")
vista.zoom = zoom
play.body.remakemask()
vista.setgrect(play.body.mask.bounds())

x0, y0 = vista.worldtoscreen((vista.wx0, vista.wy1))
x1, y1 = vista.worldtoscreen((0, 0))
x2, y2 = vista.worldtoscreen((vista.wx1, vista.wy0))

settings.vx0, settings.vy0 = 0, 0
settings.vx, settings.vy = x, y = x2 - x0, y2 - y0
pygame.display.set_caption("Map dimensions will be %sx%s...." % (x, y))

vista.vrect = pygame.Rect(0, 0, x, y)
vista.screen = vista.Surface((x, y), alpha = False)
vista.stars = [(random.randint(64, 255), random.randint(-10000, 10000), random.randint(-10000, 10000))
    for _ in range(x * y / 2000)]
vista.stars.sort()

vista.gx0 = x1-x0
vista.gy0 = y1-y0

vista.clear()
if showhexes:
    play.body.tracehexes()
play.body.draw()
for t in play.twinklers: t.draw()
for s in play.shots: s.draw()
vista.addmask(play.body.mask)

pygame.image.save(vista.screen, mapfile)



