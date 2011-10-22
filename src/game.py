# This module holds the game state, and handles saving and loading

import cPickle, os, random
import data, body, status, enemy, twinkler, vista, panels

class State(object):
    def __init__(self):
        self.body = body.Body()
        self.twinklers = []
        self.shots = []

    def think(self, dt):
        self.body.think(dt)
        self.twinklers += twinkler.newtwinklers(self.body.mask, dt)
        for t in self.twinklers:
            t.think(dt)
        self.twinklers = [t for t in self.twinklers if t.alive()]
        self.body.claimtwinklers(self.twinklers)
        self.body.attackenemies(self.shots)
        if random.random() < dt:
            self.shots += enemy.newshots(self.body)
        for s in self.shots: s.think(dt)
        self.shots = [s for s in self.shots if s.alive()]
        self.twinklers += enemy.spoils
        del enemy.spoils[:]
        self.shots += enemy.spawnedshots
        del enemy.spawnedshots[:]

    def draw(self):
        if panels.selectedtile is not None or panels.selectedorgan is not None:
            self.body.tracehexes()
        self.body.draw()
        for t in self.twinklers: t.draw()
        for s in self.shots: s.draw()
        vista.addmask(self.body.mask)
#        if cursor is not None:
#            cursor.draw()


# TODO: consider a separate directory for save games?
def savepath(filename = None):
    if filename is None: filename = "savegame.pkl"
    return data.filepath(filename)


# The following three functions must be updated together to keep them consistent
def restart():
    global state
    status.restart()
    state = State()

# TODO: save to temp file and move it only after the save is successful
def save(filename = None):
    obj = state, status.state
    cPickle.dump(obj, open(savepath(filename), "wb"))

def load(filename = None):
    global state
    fpath = savepath(filename)
    if os.path.exists(fpath):
        obj = cPickle.load(open(fpath, "rb"))
        state, status.state = obj
    else:
        restart()

    


