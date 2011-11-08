Obb
===

Entry in PyWeek #13  <http://www.pyweek.org/13/>
Team: Universe Factory 13 (unifac13)
Members: Cosmologicon (Christopher Night)


DEPENDENCIES:

You might need to install some of these before running the game:

  Python 2.6+:     http://www.python.org/
  PyGame 1.9+:     http://www.pygame.org/

You probably also need numpy installed, since the game makes heavy use
of pygame.surfarray.


RUNNING THE GAME:

On Windows or Mac OS X, locate the "run_game.pyw" file and double-click it.

Othewise open a terminal / console and "cd" to the game directory and run:

  python run_game.py

The game will take a minute to load up as the graphics engine gets started.
It may also run slowly at first, the first time it renders new objects.
Hey, I put a lot of time into that graphics engine. All things
considered, it's pretty well optimized for Pyweek. Have a little patience!

Command-line options include:

--silent
--fullscreen
--showfps (in title bar if windowed)
--restart (game is saved/loaded automatically; this overwrites the existing save)
--slow (disables some effects; use this if your computer is slow)
--doubletime (if the game is too slow-paced for you)

Default resolution is 854x480. The following command-line options change
the resolution:

--small : 640x360
--big : 1068x600
--huge : 1280x720


HOW TO PLAY THE GAME:

Use the mouse.

Scroll by dragging or use the arrow keys or WASD.

Hints and tips can be found in the file HINTS.txt

This is a sandbox game. There's no way to die and no way to win. Feel
free to quit whenever you feel like it. There are 18 organs total. If
you unlock all 18, and you survive for a few minutes with 70 or so
organs built (lower-right corner), you've seen pretty much all there is
to the game.


SOURCE CODE LICENSE:

The code for this game by Christopher Night. It's released under GPL, BSD,
MIT, WTFPL, CC-0, and any other license you want me to release it under.

The "fixes" module is by Greg Ewing. See fixes.py for details.

For license information for the assets used in this game, see the file
data/LICENSE.txt



