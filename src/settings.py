import sys


# Controls
panonpoint = False # Viewport follows mouse cursor
panonarrows = True  # Use arrow keys (or WASD) to move viewport
zoomonscroll = True  # Zoom using scroll wheel
trashonrightclick = True  # Trash a tile by right-clicking on it
panonrightclick = False   # Jump to a position by right-clicking on viewport
panondrag = True  # Move the viewport by left-click and dragging


# Overall game window
size = sx, sy = 854, 480
# Main game viewport
vsize = vx, vy = 480, 480
vx0, vy0 = 187, 0
# Tile panel (left)
psize = px, py = 187, 480
px0, py0 = 0, 0
# Status panel (right)
rsize = rx, ry = 187, 480
rx0, ry0 = 667, 0

class layout:
    meterbottom = 330
    mutagenmeterx = 120
    healmeterx = 160
    brainiconpos = -20, 486
    controlpos = 42, 450
    countsize = 60  # Font size of counters
    organcountsize = 40
    cubeiconpos = 42, 36
    ptilesize = 48 # Size of selectable tiles in the panel
    ptiley = 70  # Offset position of top tile
    buildiconsize = 40
    buildiconxs = [740, 695]


iconsize = 70
iconpos = {}
iconpos["zoomin"] = 227, 440
iconpos["zoomout"] = 627, 440
iconpos["pause"] = 227, 40
iconpos["music"] = 627, 40
iconpos["trash"] = 51, 429
iconpos["cut"] = 136, 429
iconpos["heal"] = 803, 370

maxtextwidth = 140

tzoom0 = 100  # Default tile size
zooms = 16, 24, 32, 40, 48, 60, 72
zoom0 = 48
largebuildicon = tzoom0

showstars = True
twisty = True  # Twisty paths

audiobuffer = False  # Works better for me with buffer off

fullscreen = "--fullscreen" in sys.argv
if "--slow" in sys.argv:
    showstars = False
    tzoom0 = 72

showfps = True

minfps, maxfps = 10, 60




