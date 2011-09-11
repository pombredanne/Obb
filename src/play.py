import vista, context

class Play(context.Context):
    def __init__(self):
        self.grid = vista.HexGrid()

    def think(self, dt, events, keys, mousepos, buttons):
        self.ton = self.grid.tnearest(mousepos)

    def draw(self):
        for x in range(-6, 6):
            for y in range(-6, 6):
                self.grid.drawhex((x,y))
        self.grid.drawhex(self.ton, (255, 255, 255))


