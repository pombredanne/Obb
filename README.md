Obb
===
by [Christopher Night](http://christophernight.net/) (Universe Factory games)
written for [PyWeek 13](http://www.pyweek.org/13/)

Obb is both a real-time strategy game and a tile placement puzzle game. Control the growth of a mutant named Obb. Expand into space and defend Obb from hostile forces. Collect mutagen to form new types of organs.

This game was originally written in one week for [PyWeek 13](http://www.pyweek.org/13/), the python game programming contest. This version is only slightly modified from the original.

This is a *sandbox game*. There's no way to die and no way to win. Feel free to quit when you've seen enough!

# Running the game

## Source code version (all platforms)

Install the dependencies [python 2.6+](http://www.python.org/), and [pygame 1.9+](http://www.pygame.org/), and [numpy](http://numpy.scipy.org/). (It has not been tested on python 3.) Run the following in a terminal:

`python run_game.py`

To install the dependencies on Ubuntu, you can run:

`sudo apt-get install python python-pygame python-numpy`

## Windows version

Double click on `obb.exe` 

# Controls
Use the mouse.

Quit the game at any time by pressing Esc. Your game is automatically saved.

Scroll by dragging or use the arrow keys or WASD.

Press F12 to take a screenshot.

Press F11 to make a "map" of your game. This will show your entire organism without any sidebars.

Press F9 if you want to delete your save game and start over.

# Strategy tips

Obb is both a real-time strategy game and a tile-placement puzzle game. You'll have to understand both aspects of the game to do well.

Make sure you understand what each icon does, because it might be helpful in your strategy.

# Tile placement tips

There are three colors of stalks (green, purple, and orange), and organs can only be built on stalks of the corresponding color. Purple organs are the most important, since they're how you collect resources, but green and orange organs are essential in every area. As you expand, you need to be able to build all three colors of organs in all regions. Think ahead when you're placing tiles and organs. Don't cut off any of the three colors from any part of the map. Remember that stalks can cross each other as long as it's not too dense.

Every organ terminates a stalk, so make as many branches as possible. Get in the habit of trashing most non-branching tiles you get. The non-branching pieces are really only useful if you need to get out of a tight spot or cross stalks against each other. It's fine if you're trashing more tiles than you're using. There's no rush. Remember you can trash a tile with right-click.

A single hex on the map should be put to multiple uses. Multiple stalks can go through it, and an organ can occupy the center. Use hexes as efficiently as possible. Don't hesitate to build organs over stalks or vice versa.

You can always chop pieces off and try again!

# Real-time strategy tips

Again, there's no way to win or lose. A good goal is to unlock all 18 organs, and last for a few minutes with 70 or so organs built. (The number of organs built is the first number in the lower-right.) If you do that, you'll have seen pretty much everything the game has to offer.

There are three categories of organs. Purple organs let you collect and store mutagen and ooze. Green organs let you explore new territory and control other organs. Orange organs are for defense. (Weapons are also useful for generating resources, since destroyed hazards turn into white energy.) Your main goal should be to collect and store as much mutagen as possible (the purple and blue organs), and the other organs should support this goal. The mutagen pod (the purple organ with the blue ball) is the most important - every one of these you grow unlocks a new organ.

The least essential organ is the blue cubes. They just make new tiles appear faster. But if you're stuck somewhere and you're looking for the one tile that will fit, it's much easier if you've six cubes than if you've got zero.

The amount of danger you're in depends on two things: how far out you've expanded, and how many total organs you have. The farther out an organ is from the mouth, the more it's going to be attacked. You can stay safer by building densely and evenly in all directions. Each hex can hold one organ. Try not to have too many empty hexes, and try to keep the mouth at roughly the center of your organism.

If you don't remember what an organ does, you can point to its build icon and Obb will tell you if tips are enabled. You can toggle tips by clicking on the mouth.

# License
## Source Code License

Most of the code for this game is by [Christopher Night](http://christophernight.net/). Use it however you want. It's released under [WTFPL](http://sam.zoy.org/wtfpl/), and also dedicated to the public domain under [CC-0](http://creativecommons.org/publicdomain/zero/1.0/). If you want me to release it under some other license, ask and I will.

### Developers

* [Christopher Night](http://christophernight.net/)
* Greg Ewing
* Miguel de Dios

The only exceptions are the "fixes" module by Greg Ewing, and the "fonts" module, which contains some code from pygame.org.

## Music License

Music by Kevin MacLeod, released under CC-BY. Specific songs are: Rocket, Killing Time, Itty Bitty 8 Bit, and Space Fighter Loop. Find them at [incompetech.com](http://incompetech.com/).

## Artwork License

Most of the graphics are procedurally generated by the code, and are under the same license as the code. Icons are based on CC0 (public domain) clip art from [openclipart.org](http://www.openclipart.org/). Specifically:

* [Red axe](http://www.openclipart.org/detail/85753/red-axe-by-inky2010)
* [Trash can](http://www.openclipart.org/detail/68/trash-can-by-andy)
* [Treble clef](http://www.openclipart.org/detail/3344/treble-clefs-by-zeimusu-3344)
* [Zoom icons](http://www.openclipart.org/detail/88045/simple-zoom-icons-by-snifty)
* [Heart ECG](http://www.openclipart.org/detail/154117/heart-ecg-logo-by-juliobahar) 

## Font License

[I suck at golf](http://www.fontspace.com/divide-by-zero/i-suck-at-golf) by Divide by Zero.

See the file `data/suckgolf-README.TXT` for license information

## Sound License

Sounds were resampled from the following freesound.org sources:

* [Pumpkin Guts Long](http://www.freesound.org/people/MWLANDI/sounds/85861/) by MWLANDI - CC-SAMPLING+
* [Lazer](http://www.freesound.org/people/THE_bizniss/sounds/39459/) by THE bizniss - CC-SAMPLING+
* [Thud](http://www.freesound.org/people/farbin/sounds/36787/) by farbin - CC-SAMPLING+
* [shields3](http://www.freesound.org/people/PhreaKsAccount/sounds/46494/) by PhreaKsAccount - CC-SAMPLING+ 
