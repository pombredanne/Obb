# This module keeps track of the game state pieces that aren't properties
#   of entities, such as the amount of mutagen and ooze and available tiles

import mechanics

class State(object):
	def __init__(self):
		# Appspecs for hexagonal tiles with stalks on them
		self.tiles = [self.newtile(c) for c in range(mechanics.ntiles)]
		# The "time" remaining to load for each of the tiles. These times
		#   may actually count down different from clock time, depending
		#   on how many cubes you have.
		self.tiletimes = [2 + 0.4 * j for j in range(mechanics.ntiles)]
		self.tileloadrate = mechanics.baseloadrate
		self.ncubes = 0
		# Organs use control, brains grant control
		self.control = 0
		self.maxcontrol = 0
		# Amount of mutagen (used for adding organs)
		self.mutagen = self.maxmutagen = mechanics.mutagen0
		# Amount of ooze (used for healing)
		self.ooze = self.maxooze = mechanics.ooze0
	
	
	def newtile(self, n):
		return mechanics.randomspec("app%s" % mechanics.tilecolors[n])        
	
	
	def getnewtile(self, n):
		self.tiles[n] = self.newtile(n)
		self.tiletimes[n] = mechanics.tileloadtime
	
	
	def setmaxmutagen(self, maxmutagen):
		# TODO: incorporate mutagen limit from mechanics
		self.maxmutagen = maxmutagen
		self.mutagen = min(self.mutagen, self.maxmutagen)
	
	
	def setmaxooze(self, maxooze):
		self.maxooze = maxooze
		self.ooze = min(self.ooze, self.maxooze)
	
	
	def addmutagen(self, dmutagen):
		self.mutagen = max(min(self.mutagen + dmutagen, self.maxmutagen), 0)
	
	
	def addooze(self, dooze):
		self.ooze = max(min(self.ooze + dooze, self.maxooze), 0)
	
	
	def think(self, dt):
		self.tileloadrate = mechanics.baseloadrate + mechanics.cubeloadrate * self.ncubes
		for j in range(len(self.tiletimes)):
			self.tiletimes[j] = max(self.tiletimes[j] - self.tileloadrate * dt, 0)
		addmutagen(mechanics.basemutagenrate * dt)
		addooze(mechanics.baseoozerate * dt)


def restart():
	global state
	state = State()


def addpart(part, m = 1):
	"""Call this when a part is activated to add its tallies to the totals"""
	state.control += m * part.control
	state.maxcontrol += m * part.maxcontrol
	state.maxmutagen += m * part.maxmutagen
	state.maxooze += m * part.maxooze
	state.ncubes += m * part.ncubes


def removepart(part):
	"""Call this when a part is deactivated"""
	addpart(part, -1)


def enoughcontrol(part):
	"""
	Do we have enough control to add this part?
	"""
	if not part.control: return True  # none needed
	
	return state.control + part.control <= state.maxcontrol


def addmutagen(dmutagen):
	state.addmutagen(dmutagen)


def addooze(dooze):
	state.addooze(dooze)


def usemutagen(dmutagen):
	state.addmutagen(-dmutagen)


def useooze(dooze):
	state.addooze(-dooze)