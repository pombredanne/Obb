# Settings that relate to the game mechanics

import random
import vista, settings

from i18n import _

vthreshold = 0.2  # Visibility threshold
twinklerrate = 0.004  # Twinklers per unit area per second
mutagenhit = 6  # How much you get when a twinkler hit a mutagenitor
oozehit = 5

# TODO: incorporate limits on mutagen and ooze
basemutagenrate = 0.5  # How fast it rises on its own
baseoozerate = 0.3
mutagen0 = 65  # Base amount
mutagenmax = 300
if settings.unlockall:
    mutagen0 = mutagenmax
ooze0 = 20
mutagenpodsize = 15
oozepodsize = 15
tileloadtime = 12.
baseloadrate = 1.
cubeloadrate = 0.6
shieldradius = 4
bulbrange = 10
zotterrange = 4
zotterdhp = 3
bulbdhp = 2
stardhp = 1
starrange = 6

eyelightradius = 7
corelightradius = 7
braincontrol = 6  # How much maxcontrol a brain gives you
corecontrol = 6   # How much maxcontrol you start with

ntiles = 6
tilecolors = [0, 0, 1, 1, 2, 2]

# Permissable dedges for tiles
#dedgesets = [(1,), (2,), (4,), (5,),
#    (1,2), (1,3), (1,4), (1,5), (2,3), (2,4), (2,5), (3,4), (3,5), (4,5),
#    (1,2,3), (1,2,4), (1,2,5), (1,3,4), (1,3,5), (1,4,5),
#        (2,3,4), (2,3,5), (2,4,5), (3,4,5)]

dedgesets = ([(1,), (5,), (1,3), (3,5), (1,4), (2,5), (2,), (3,), (4,)] +
            [(2,3), (2,4), (3,4)] * 2)



class AppendageSpec(object):
    """Data to specify the path of an appendage, irrespective of starting position"""
    def __init__(self, dedges, color):
        self.dedges = sorted(set(dedges))
        self.color = color
    
    def outbuds(self, pos, edge):
        return [vista.grid.opposite(pos, edge + dedge) for dedge in self.dedges]


def randomspec(color = None):
    dedges = random.choice(dedgesets)
    if len(dedges) > 2: dedges = random.choice(dedgesets)
    if color is None: color = "app%s" % random.choice((0,1,2))
    return AppendageSpec(dedges, color)


# TODO: move this into a CSV data file

# Colors determine where you can build organs
# Because of graphical limitations, giant versions should have the same
#   colors as their regular versions
colors = {}

# Monitor/oversee
colors["eye"] = "app0"
colors["brain"] = "app0"
colors["giantbrain"] = "app0"
colors["eyebrain"] = "app0"
colors["tripleeye"] = "app0"

# Attack/defend
colors["shield"] = "app1"
colors["bulb"] = "app1"
colors["star"] = "app1"
colors["zotter"] = "app1"

# Build/heal
colors["mutagenitor"] = "app2"
colors["giantmutagenitor"] = "app2"
colors["mutagenpod"] = "app2"
colors["giantmutagenpod"] = "app2"
colors["plasteritor"] = "app2"
colors["giantplasteritor"] = "app2"
colors["plasterpod"] = "app2"
colors["giantplasterpod"] = "app2"
colors["cube"] = "app2"


costs = {
         "mutagenitor": 20,
           "eye": 35,
             "brain": 50,
         "mutagenpod": 65,
           "plasteritor": 80,
             "zotter": 95,
         "cube": 110,
           "plasterpod": 125,
             "bulb": 140,
         "shield": 155,
           "eyebrain": 170,
             "giantmutagenpod": 185,
         "tripleeye": 200,
           "giantbrain": 215,
             "giantmutagenitor": 230,
         "giantplasterpod": 245,
           "giantplasteritor": 260,
             "star": 275,
         }

info = {}
info["eye"] = _("this organ let me see the space around it. me no can grow where me no can see")
info["brain"] = _("this organ let me control other organs. no can grow organs if me no have enough brains")
info["giantbrain"] = _("biggest brain is best brain!")
info["eyebrain"] = _("it eye! it brain! it both!")
info["tripleeye"] = _("this organ let me see out even farther! sometimes me get dizzy")

info["shield"] = _("this organ for protection. it block half of incoming danger")
info["bulb"] = _("this weapon good for rapid, long range fire, but it only shoot in one direction")
info["star"] = _("this weapon absorb white energy and make wave of destruction!")
info["zotter"] = _("this weapon good for short-range attacks")

info["mutagenitor"] = _("this organ absorb white energy and make mutagen. very important!")
info["mutagenpod"] = _("this organ hold more mutagen. me need to be able to hold more mutagen before me can grow more advanced organs")
info["plasteritor"] = _("this organ absorb white energy and make ooze. me need ooze to heal")
info["plasterpod"] = _("this organ hold more ooze. more ooze help me survive big attacks")
info["giantmutagenitor"] = _("this organ absorb white energy and make even more mutagen!")
info["giantmutagenpod"] = _("this organ hold lots of mutagen")
info["giantplasteritor"] = _("this organ absorb white energy and make even more ooze!")
info["giantplasterpod"] = _("this organ hold lots of healing ooze")
info["cube"] = _("this organ control how fast new stalk options appear. more of this organ means options appear faster!")

assert set(colors) == set(costs)
assert set(costs) == set(info)



