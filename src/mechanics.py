import random
import vista

vthreshold = 0.3  # Visibility threshold
twinklerrate = 0.001  # Twinklers per unit area per second
mutagenhit = 20  # How much you get when a twinkler hit a mutagenitor
basemutagenrate = 4  # How fast it rises on its own
basehealrate = 4

# Permissable dedges for tiles
# Conspicuous in its absense is a straight piece
dedgesets = [(1,), (2,), (4,), (5,),
    (1,2), (1,3), (1,4), (1,5), (2,3), (2,4), (2,5), (3,4), (3,5), (4,5),
    (1,2,3), (1,2,4), (1,2,5), (1,3,4), (1,3,5), (1,4,5),
        (2,3,4), (2,3,5), (2,4,5), (3,4,5)]

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
colors = {}

# Monitor/oversee
colors["eye"] = "app0"
colors["brain"] = "app0"
colors["eyebrain"] = "app0"
colors["tripleeye"] = "app0"

# Attack/defend
colors["coil"] = "app1"
colors["bulb"] = "app1"
colors["star"] = "app1"

# Build/heal
colors["mutagenitor"] = "app2"
colors["ball"] = "app2"
colors["cube"] = "app2"


#costs = {"eye":30, "brain":60, "eyebrain": 120, "mutagenitor":80, "tripleeye": 0, "coil":20, "ball":50, "cube": 10}
costs = {"bulb":10}


