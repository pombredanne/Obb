# Draw the side panels, handle mouse events in these regions, and keep track
#   of what body part we have selected, if any

import vista, settings, mechanics, status, graphics

selectedtile = None
selectedorgan = None
buildrects = {}

def tilepos(jtile):
    cx = int(settings.px / 2 + (0.85 if jtile % 2 else -0.85) * settings.layout.ptilesize)
    cy = int(settings.layout.ptiley + (1 + 0.95 * jtile) * settings.layout.ptilesize)
    return cx, cy


def getlevel(h):
    """Return the pixel height correpsonding to a given meter amount"""
    # TODO: rethink how the height is determined
    p = int(settings.layout.metermaxy * h / mechanics.mutagenmax)
    return min(p, settings.layout.metermaxy)


def draw():
    # TODO: see how much of a speedup we get by caching the images here
    drawtiles()
    drawmutagenmeter()
    drawoozemeter()
    drawbuildicons()

def drawtiles():
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

def drawmutagenmeter():
    height = getlevel(status.state.maxmutagen)
    level = getlevel(status.state.mutagen)
    img = graphics.meter(graphics.helixmeter(height), level, graphics.colors["mutagen"])
    rect = img.get_rect()
    rect.midbottom = midbottom = settings.layout.mutagenmeterx, settings.layout.meterbottom
    vista.rsurf.blit(img, rect)

def drawoozemeter():
    height = getlevel(status.state.maxooze)
    level = getlevel(status.state.ooze)
    img = graphics.meter(graphics.stalkmeter(height), level, graphics.colors["ooze"])
    rect = img.get_rect()
    rect.midbottom = midbottom = settings.layout.oozemeterx, settings.layout.meterbottom
    vista.rsurf.blit(img, rect)

def drawbuildicons():
    global buildrects
    buildrects = {}  # remember for pointing and clicking purposes
    otypes = sorted(mechanics.costs.items(), key = lambda (k,v): v)
    for j, (otype, cost) in enumerate(otypes):
        if status.state.maxmutagen < cost: continue
        x = settings.layout.buildiconxs[j % len(settings.layout.buildiconxs)]
        y = settings.layout.meterbottom - getlevel(cost)
        img = graphics.icon(otype)
        if status.state.mutagen < cost:
            img = graphics.ghostify(img)
        elif otype == selectedorgan:
            img = graphics.brighten(img)
        rect = img.get_rect(center = (x, y))
        buildrects[otype] = rect
        vista.addoverlay(img, rect)

def iconpoint((mx, my)):
    """Return the index (int) of any tiles at this position, or the name
    (str) of any build icons at this position, or None"""
    for jtile in range(mechanics.ntiles):
        cx, cy = tilepos(jtile)
        if (mx - cx) ** 2 + (my - cy) ** 2 < settings.layout.ptilesize ** 2:
            return jtile
    for otype, rect in buildrects.items():
        if rect.collidepoint((mx, my)):
            return otype
    return None

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



