import vista, context

class Play(context.Context):
    def __init__(self):
        self.grid = vista.HexGrid()

    def draw(self):
        for x in range(-6, 6):
            for y in range(-6, 6):
                self.grid.drawhex((x,y))


