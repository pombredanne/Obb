# This module holds the game state, and handles saving and loading

import cPickle, os, random
import context, settings, data, body, panel, status, enemy, twinkler, vista

class State(object):
    def __init__(self):
        self.body = body.Body()
        self.panel = panel.Panel(self.body)
        self.status = status.Status(self.body)
        self.twinklers = []
        self.shots = []

    def think(self, dt, mousepos):
        self.body.think(dt, self.status.healmeter)
        self.panel.think(dt)
        self.status.think(dt, mousepos)
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
        self.status.setheights(self.body.maxmutagen, self.body.maxplaster)
        self.status.mutagenmeter.amount += self.body.checkmutagen()
        self.status.healmeter.amount += self.body.checkplaster()
        self.twinklers += enemy.spoils
        del enemy.spoils[:]
        self.shots += enemy.spawnedshots
        del enemy.spawnedshots[:]
    def draw(self):
        if self.panel.selected is not None or self.status.selected is not None:
            self.body.tracehexes()
        self.body.draw()
        for t in self.twinklers: t.draw()
        for s in self.shots: s.draw()
        vista.addmask(self.body.mask)
#        if cursor is not None:
#            cursor.draw()
        self.panel.draw()
        self.status.draw()



def restart():
    global state
    state = State()

# TODO: consider a separate directory for save games?
def savepath(filename = None):
    if filename is None: filename = "savegame.pkl"
    return data.filepath(filename)

def save(filename = None):
    cPickle.dump(state, open(savepath(filename), "wb"))

def load(filename = None):
    global state
    fpath = savepath(filename)
    if os.path.exists(fpath):
        state = cPickle.load(open(fpath, "rb"))
    else:
        restart()

    


