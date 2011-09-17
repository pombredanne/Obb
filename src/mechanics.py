import random
import vista

vthreshold = 0.2  # Visibility threshold
twinklerrate = 0.002  # Twinklers per unit area per second
mutagenhit = 5  # How much you get when a twinkler hit a mutagenitor
plasterhit = 5
basemutagenrate = 1  # How fast it rises on its own
basehealrate = 1
mutagen0 = 60  # Base amount
plaster0 = 20
mutagenpodamount = 20
plasterpodamount = 20
baseloadrate = 0.5
cubeloadrate = 0.3

# Permissable dedges for tiles
#dedgesets = [(1,), (2,), (4,), (5,),
#    (1,2), (1,3), (1,4), (1,5), (2,3), (2,4), (2,5), (3,4), (3,5), (4,5),
#    (1,2,3), (1,2,4), (1,2,5), (1,3,4), (1,3,5), (1,4,5),
#        (2,3,4), (2,3,5), (2,4,5), (3,4,5)]

dedgesets = ([(1,), (5,), (1,3), (3,5)] +
            [(2,), (3,), (4,)] * 2 +
            [(2,3), (2,4), (3,4)] * 3)



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


costs = {"mutagenitor":10, "zotter":20, "cube":30}
costs = {"plasteritor":10, "giantplasteritor": 20}

costs = {"eye":30, "brain":60, "eyebrain": 120, "mutagenitor":80, "tripleeye": 0, "coil":20, "ball":50, "cube": 10}

costs = {"mutagenpod": 30, "eye": 40, "brain": 50, "mutagenitor": 20,
         "plasterpod": 70, "cube": 80, "star": 100, }

info = {}
info["eye"] = "this organ let me see out farther. me no can grow where me no can see"
info["brain"] = "me need this organ to work other organs"
info["giantbrain"] = "biggest brain is best brain!"
info["eyebrain"] = "it eye! it brain! it both!"
info["tripleeye"] = "me see way far out with this. sometimes me get dizzy"

info["mutagenitor"] = "this organ absorb white energy and make mutagen. very important!"
info["mutagenpod"] = "this organ hold more mutagen. me need this to grow more advanced organs"
info["plasteritor"] = "this organ absorb white energy and make ooze. me need ooze to heal"
info["plasterpod"] = "this organ hold more ooze, help me survive big attacks"
info["cube"] = "want stalk options to appear faster? grow this organ!"





