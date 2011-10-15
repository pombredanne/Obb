import sys

# Attention players: I can't guarantee that the game will run properly
# if you mess with these settings. I haven't tested every possible
# combination. These settings are here for my benefit.

# Having said that, feel free to mess with these settings. :)
# At the very least, if you change any of the settings, you should
#   restart the game with --restart


# Controls
panonpoint = False # Viewport follows mouse cursor
panonarrows = True  # Use arrow keys (or WASD) to move viewport
zoomonscroll = True  # Zoom using scroll wheel
trashonrightclick = True  # Trash a tile by right-clicking on it
panonrightclick = False   # Jump to a position by right-clicking on viewport
panondrag = True  # Move the viewport by left-click and dragging


tzoom0 = 144  # Default tile size
zooms = 16, 24, 32, 40, 48, 60, 72
largebuildicon = tzoom0

def setresolution(x, y = None):
    global sx, sy, size
    global vx, vy, vsize, vx0, vy0
    global px, py, psize, px0, py0
    global rx, ry, rsize, rx0, ry0
    global layout, iconsize, iconpos
    global maxtextwidth, maxblockwidth, zoom0

    if y is None:  # only vertical resolution specified
        x, y = int(math.ceil(8. * x / 9)) * 2, x
    sx, sy = x, y
    fac = float(y) / 480
    def f(*args):
        return int(fac * args[0]) if len(args) == 1 else [int(fac*arg) for arg in args]
    size = sx, sy
    # Main game viewport
    vsize = vx, vy = f(480), sy
    vx0, vy0 = f(187), 0
    # Tile panel (left)
    psize = px, py = vx0, sy
    px0, py0 = 0, 0
    # Status panel (right)
    rsize = rx, ry = sx - px - vx, sy
    rx0, ry0 = px + vx, 0

    class layout:
        meterbottom = f(330)
        mutagenmeterx = f(124)
        oozemeterx = f(160)
        metermaxy = f(300)
        brainiconpos = f(-20, 486)
        controlpos = f(42, 450)
        countsize = f(60)  # Font size of counters
        tipsize = f(32)  # Font size of tips
        tipmargin = f(20)
        organcountsize = f(40)
        cubeiconpos = f(42, 36)
        ptilesize = f(48) # Size of selectable tiles in the panel
        ptiley = f(70)  # Offset position of top tile
        tilerollx = f(300)
        buildiconsize = f(36)
        buildiconxs = f(752, 752-36, 752-2*36)

    iconsize = f(70)
    iconpos = {}
    iconpos["zoomin"] = f(227, 440)
    iconpos["zoomout"] = f(627, 440)
    iconpos["pause"] = f(227, 40)
    iconpos["music"] = f(627, 40)
    iconpos["trash"] = f(51, 429)
    iconpos["cut"] = f(136, 429)
    iconpos["heal"] = f(803, 370)

    maxtextwidth = f(140)
    maxblockwidth = f(420)

    zoom0 = max(z for z in zooms if z <= f(48))

if "--micro" in sys.argv:
    setresolution(428, 240)
elif "--small" in sys.argv:
    setresolution(640, 360)
elif "--big" in sys.argv:
    setresolution(1068, 600)
elif "--huge" in sys.argv:
    setresolution(1280, 720)
else:
    setresolution(854, 480)

showstars = True
twisty = True  # Twisty paths

audiobuffer = False  # Works better for me with buffer off
soundvolume = 0.5

showtips = True


silent = "--silent" in sys.argv or "--nosound" in sys.argv
restart = "--restart" in sys.argv
fullscreen = "--fullscreen" in sys.argv
barrage = "--barrage" in sys.argv  # Loads of enemies. Not fun.
if "--slow" in sys.argv:
    showstars = False
    tzoom0 = 72
fast = "--doubletime" in sys.argv    

# Cheat
unlockall = "--unlockall" in sys.argv   # Will probably only work if you restart
debugkeys = True

showfps = "--showfps" in sys.argv
saveonquit = True
autosave = True
savetimer = 15  # seconds between autosaves

minfps, maxfps = 10, 60




