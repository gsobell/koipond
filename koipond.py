#!/usr/bin/env python3
import sys   # for help message
import curses
import time
import random
from curses import wrapper
# import vlc # for radio

PADS_TO_GEN = 10
PADS_MAX_SIZE = 4
KOI_TO_GEN = 8
KOI_MAX_SIZE = 5
KOI_MIN_SIZE = 3
REST = (0, 0)
PROB_MOVE = 5   # continue same direction
PROB_REST = 10  # relaxed fish
FPS = 5
"""
A curses program that displays a koi pond
allow pad for user to scroll around pond, parallax
"""

"""
Notes on curses:
Legal coordinates will then extend
from (0,0) to (curses.LINES - 1, curses.COLS - 1).
Consider calling max height each times in case term resize
For now, assume, no resize during program run
"""

# TODO
# collisions
# better graphics for fish


def show_usage():
    print("usage: python koipond.py [options]")
    print("Options:")
    print(" -k,  --koi    koi to generate")
    print(" -p,  --pads   lily pads to generate")
    print(" -f,  --fps    frames per second")
    print(" -h,  --help   display this help message")
    print(" -v,           print version number.")


def flag_error():
    print("One or more arguments are invalid.")
    show_usage()
    sys.exit()


# Check if flags present
i = 1
while i < len(sys.argv):
    arg = sys.argv[i]
    if arg == "-h" or arg == "--help":
        print("koipond.py")
        print("a koi pond for your terminal")
        show_usage()
        sys.exit()
    if arg == "-v":
        print("version 0.0.1")
        sys.exit()
    try:
        if arg == "-p" or arg == "--pads":
            PADS_TO_GEN = int(sys.argv[i+1])
        if arg == "-k" or arg == "--koi":
            KOI_TO_GEN = int(sys.argv[i+1])
        if arg == "-f" or arg == "-fps":
            FPS = float(sys.argv[i+1])
    except ValueError:
        flag_error()
    i += 1


class School:
    def __init__(self, stdscr):
        self.RED = curses.color_pair(3)
        self.BLACK = curses.color_pair(4)
        self.WHITE = curses.color_pair(5)
        self.colors = (self.RED, self.BLACK, self.WHITE)
        self.directions = [(0, 0), (0, 1), (1, 0), (0, -1), (-1, 0)]
        self.koi = []
        for k in range(KOI_TO_GEN):
            koi_y = random.randrange(
                KOI_MAX_SIZE, curses.LINES - KOI_MAX_SIZE - 1)
            koi_x = random.randrange(
                KOI_MAX_SIZE, curses.COLS - KOI_MAX_SIZE - 1)
            koi_size = random.randrange(2, KOI_MAX_SIZE)
            koi_color = [random.choice(self.colors)
                         for cell in range(koi_size)]
            koi_direction = random.choice(
                [d for d in self.directions if d is not REST])
            self.koi.append(self.Koi((koi_y, koi_x),
                                     koi_size,
                                     koi_color,
                                     koi_direction))
        for fish in self.koi:
            for k, cell in enumerate(fish.cells):
                if not k:
                    stdscr.addstr(cell[0], cell[1], fish.face, fish.color[k])
                else:
                    stdscr.addstr(cell[0], cell[1], ". ", fish.color[k])
            stdscr.refresh()

    def new_direction(self, fish):
        new_direction = random.choices(self.directions,
                                       weights=[1 if choice != fish.direction
                                                else PROB_REST
                                                if choice == REST
                                                else 0 if
                                                (choice[0]
                                                 + fish.direction[0]
                                                 and choice[1]
                                                 + fish.direction[1]) == 0
                                                else PROB_MOVE for
                                                choice in self.directions],
                                       k=1).pop()
        for cell in fish.cells:
            y = cell[0] + new_direction[0]
            x = cell[1] + new_direction[1]
            if (curses.LINES - 2 > y > 0) and (curses.COLS - 2 > x > 0):
                return new_direction
            return None

    def update(self, stdscr):
        for fish in self.koi:
            new_direction = None
            while not (new_direction):
                new_direction = self.new_direction(fish)
            if new_direction == REST:
                fish.direction = new_direction
                continue
            fish.cells.insert(0,
                              (fish.cells[0][0] + new_direction[0],
                               fish.cells[0][1] + new_direction[1]))
            tail = fish.cells.pop()
            for k, cell in enumerate(fish.cells):
                stdscr.addstr(tail[0], tail[1], "  ", curses.color_pair(1))
            for k, cell in enumerate(fish.cells):
                if k == 0:
                    stdscr.addstr(cell[0], cell[1], fish.face, fish.color[k])
                else:
                    # draw face again in case covered
                    stdscr.addstr(cell[0], cell[1], "  ", fish.color[k])
            stdscr.addstr(fish.cells[0][0], fish.cells[0]
                          [1], fish.face, fish.color[0])
            fish.direction = new_direction
        stdscr.refresh()

    class Koi:
        def __init__(self, head, size, colors, direction):
            self.head = head
            self.cells = [[head[0] + direction[0] * k,
                           head[1] + direction[1] * k] for k in range(1, size)]
            self.size = size
            self.color = colors
            self.direction = direction
            self.face = "··"
            # self.face_update(self.direction)
        #
        # def face_update(self, direction):
        #     if direction == [0, 1]:
        #         self.face = " :"
        #     if direction == [0, -1]:
        #         self.face = ": "
        #     if direction == [1, 0]:
        #         self.face = ".."
        #     if direction == [-1, 0]:
        #         self.face = ".."
        #     return self.face


class Lilies:
    def __init__(self, stdscr):
        lilies = []
        for p in range(PADS_TO_GEN):
            pad_y = random.randrange(curses.LINES - PADS_MAX_SIZE - 1)
            pad_x = random.randrange(curses.COLS - PADS_MAX_SIZE - 1)
            pad_size = random.randrange(PADS_MAX_SIZE)
            lilies.append(self.Lily(pad_y, pad_x, pad_size))
        for lily in lilies:
            for cell in lily.cells:
                stdscr.addstr(cell[0],
                              cell[1],
                              ". ", curses.color_pair(2)
                              )
                stdscr.refresh()

    class Lily:
        def __init__(self, pad_y, pad_x, pad_size):
            self.y = pad_y
            self.x = pad_x
            self.size = pad_size
            self.cells = [(col, row)
                          for col in range(pad_y, pad_y + pad_size)
                          for row in range(pad_x, pad_x + pad_size)]


def setup(stdscr):
    """Sets up the screen and paints the pond blue"""
    stdscr.clear()   # Clear the screen
    curses.noecho()  # Turn off echoing of keys
    curses.cbreak()
    stdscr.keypad(True)   # Enable keypad mode
    curses.curs_set(0)    # Hide cursor
    curses.start_color()  # Enable colors if supported
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
    stdscr.bkgd(' ', curses.color_pair(1))
    stdscr.refresh()


def main(stdscr):
    max_y, max_x = stdscr.getmaxyx()  # Get the size of the terminal
    setup(stdscr)
    Lilies(stdscr)
    school = School(stdscr)
    while True:
        school.update(stdscr)
        time.sleep(FPS**-1)
        stdscr.refresh()
    stdscr.getch()  # wait to exit


if __name__ == "__main__":
    try:
        wrapper(main)
    except KeyboardInterrupt:
        print("Thank you for visiting the pond.")
