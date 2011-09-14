import sys

# Overall game window
size = sx, sy = 854, 480
# Main game viewport
vsize = vx, vy = 480, 480
vx0, vy0 = 187, 0
# Tile panel
psize = px, py = 187, 480
px0, py0 = 0, 0

tzoom0 = 120  # Default tile size (should be rather large)
zooms = 16, 24, 32, 40, 48, 60
ptilesize = 60 # Size of selectable tiles in the panel

fullscreen = "--fullscreen" in sys.argv
showfps = True

minfps, maxfps = 10, 60




