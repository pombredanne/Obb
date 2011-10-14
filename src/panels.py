# Draw the side panels, handle mouse events in these regions, and keep track
#   of what body part we have selected, if any

import vista, settings, mechanics, status, graphics

selectedtile = None
selectedorgan = None

def tilepos(jtile):
    cx = int(settings.px / 2 + (0.85 if jtile % 2 else -0.85) * settings.layout.ptilesize)
    cy = int(settings.layout.ptiley + (1 + 0.95 * jtile) * settings.layout.ptilesize)
    return cx, cy

def draw():
    # Draw the tiles
    loadrate = status.state.tileloadrate
    for j in range(mechanics.ntiles):
        tiletime = status.state.tiletimes[j]
        color = "app" + str(mechanics.tilecolors[j])
        appspec = status.state.tiles[j]
        cx, cy = tilepos(j)
        if tiletime <= 0:  # Draw it in its normal place
            img = graphics.drawpaneltile(appspec.dedges, color)
            if j == selectedtile:
                img = graphics.brighten(img)
        elif tiletime <= loadrate:  # Draw it rolling in from the left
            frac = float(tiletime) / loadrate
            cx -= int(frac * settings.layout.tilerollx)
            img = graphics.drawpaneltile(appspec.dedges, color, tilt = -450 * frac)
        else:  # Draw the progress bar
            part = float(mechanics.tileloadtime - tiletime)
            full = float(mechanics.tileloadtime - loadrate)
            assert 0 <= part <= full
            img = graphics.loadbar(part / full if full else 0, color)
        rect = img.get_rect(center = (cx, cy))
        vista.psurf.blit(img, rect)
    # Draw the meters
    # TODO
    # Add the organ icons to the vista queue
    # TODO


def iconpoint((mx, my)):
    """Return the index (int) of any tiles at this position, or the name
    (str) of any build icons at this position, or None"""
    for jtile in range(mechanics.ntiles):
        cx, cy = tilepos(jtile)
        if (mx - cx) ** 2 + (my - cy) ** 2 < settings.layout.ptilesize ** 2:
            return jtile
    return None
    # TODO organ clickage

def selecticon(iconname = None):
    """Click on the specified tile or build icon"""
    global selectedtile, selectedorgan
    if iconname in range(mechanics.ntiles) and iconname != selectedtile:
        selectedtile = iconname
    else:
        selectedtile = None
    if iconname in mechanics.costs and iconname != selectedorgan:
        selectedorgan = iconname
    else:
        selectedorgan = None

def claimtile(jtile = None):
    """Remove the given tile (or the selected tile if there's none"""
    if jtile is None: jtile = selectedtile
    status.state.getnewtile(jtile)

def claimorgan(otype = None):
    """Use the mutagen associated with the given organ type"""
    if otype is None: otype = selectedorgan
    status.usemutagen(mechanics.costs[otype])



