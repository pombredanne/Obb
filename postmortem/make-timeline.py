import pygame

pygame.init()
screen0 = pygame.display.set_mode((520, 280))
screen = pygame.Surface((520, 300), pygame.SRCALPHA)

timeline = pygame.Surface((24*9*20, 20))
lastt = 0
ts = [0]
tasks = [""]
for line in open("timeline.txt"):
    line = line.strip()
    if not line: continue
    h = int(line[0:2])
    m = int(line[3:5])
    task = line[6:].strip()
    t = h + m / 60.
    while t < lastt:
        t += 24.
    lastt = t
    ts.append(t)
    tasks.append(task)

ts.append(24*8)

colors = {}
colors[""] = 0, 0, 0
colors["code"] = 0, 64, 0
colors["sleep"] = 32, 32, 32
colors["stop"] = 64, 0, 0
colors["job"] = 0, 0, 64

tally = {}
codetally = [0] * 8

for j in range(len(tasks)):
    x0, x1 = int(ts[j] * 20), int(ts[j+1] * 20)
    rect = pygame.Rect(x0, 0, x1 - x0, 20)
    timeline.fill(colors[tasks[j]], rect)
    if tasks[j] not in tally: tally[tasks[j]] = 0
    tally[tasks[j]] += ts[j+1] - ts[j]
    if tasks[j] == "code":
        codetally[int((ts[j+1]-6)/24.)] += ts[j+1] - ts[j]
    if tasks[j] == "sleep":
        print "sleep", ts[j+1] - ts[j]

for line in open("../hg-log.txt"):
    if not line.startswith("date"): continue
    d, h, m = int(line[21:23]), int(line[24:26]), int(line[27:29])
    t = (d - 10) * 24 + h + m / 60.
    x = int(t * 20)
    pygame.draw.line(timeline, (0, 128, 0), (x, 0), (x, 20))

print tally
print codetally


daynames = ["Saturday 9/10", "Sunday 9/11", "Monday 9/12", "Tuesday 9/13",
  "Wednesday 9/14", "Thursday 9/15", "Friday 9/16", "Saturday 9/17"]
font = pygame.font.Font(None, 40)



timebox = pygame.Surface((24*20, 22 * 8), pygame.SRCALPHA)
for j in range(8):
    timebox.blit(timeline, (-(j*24+6)*20, 22*j))
    day = font.render(daynames[j], True, (255, 255, 255))
    day = pygame.transform.smoothscale(day, (day.get_width(), day.get_height()/2))
    a = pygame.surfarray.pixels_alpha(day)
    a /= 4
    del a
    timebox.blit(day, day.get_rect(center = (12*20, 11+22*j)))

hfont = pygame.font.Font(None, 16)
for x in range(0,25,3):
    h = (x + 6) % 24
    s = str(h % 12 or 12) + ("am" if h < 12 else "pm")
    text = hfont.render(s, True, (64, 64, 64))
    screen.blit(text, text.get_rect(midbottom = (20 + 20 * x, 24)))
    
screen.blit(timebox, (20,30))
for j in range(25):
    x = 20 + j * 20
    pygame.draw.line(screen, (255, 255, 255, 60), (x, 28), (x, 30 + 22 * 8))


for j, (caption, color) in enumerate([("game", "code"), ("sleep", "sleep"), ("job", "job")]):
    text = font.render(caption, True, (255, 255, 255))
    text = pygame.transform.smoothscale(text, (text.get_width(), text.get_height()/2))
    legend = pygame.Surface((100, 20))
    legend.fill(colors[color])
    a = pygame.surfarray.pixels_alpha(text)
    a /= 4
    del a
    legend.blit(text, text.get_rect(center = (50, 10)))
    screen.blit(legend, (100, 216+22*j))

screen0.blit(screen, (0, -6))

pygame.image.save(screen0, "obb-dev-timeline.png")

pygame.display.flip()

while not any(event.type == pygame.KEYDOWN for event in pygame.event.get()):
    pass



