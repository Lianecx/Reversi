import curses
import math
from curses import wrapper

MOVE_KEYS = [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN]


class Reversi:

    def __init__(self, size, stdscr):
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_WHITE)

        self.stdscr = stdscr
        self.size = size
        self.field = [[None for i in range(self.size)] for j in range(self.size)]
        # Set the 4 stones at the beginning

        middle_x = math.floor(self.size / 2)
        middle_y = math.floor(self.size / 2)

        self.field[middle_x][middle_y] = 1
        self.field[middle_x - 1][middle_y - 1] = 1
        self.field[middle_x][middle_y - 1] = 2
        self.field[middle_x - 1][middle_y] = 2
        self.highlight = [middle_x, middle_y]

        self.player = 1

    # The following function draws the gamegrid on the terminal.
    def render(self):
        self.stdscr.clear()
        self.stdscr.addstr('    ')
        self.stdscr.addstr(f'Player {self.player}\'s turn\n', curses.color_pair(2))

        # Top row (0 1 2 3 4 5 6 7 ...)
        self.stdscr.addstr('  ')
        for i in range(self.size):
            self.stdscr.addstr(f'{chr(65 + i)} ')
        self.stdscr.addstr('\n')
        # The rest of the rows
        for i in range(self.size):
            self.stdscr.addstr(f'{i} ')
            for j in range(self.size):
                color = curses.color_pair(1) | curses.A_REVERSE if self.highlight == [i, j] else curses.A_NORMAL
                if self.field[i][j] == 1:
                    self.stdscr.addstr('X', color)
                elif self.field[i][j] == 2:
                    self.stdscr.addstr('O', color)
                else:
                    self.stdscr.addstr('.', color)
                self.stdscr.addstr(' ')
            self.stdscr.addstr('\n')
        self.stdscr.refresh()

    def start_game(self):
        self.render()
        while True:
            if self.check_end():
                # End the game
                self.stdscr.getch()
                return

            key = self.stdscr.getch()
            if key == curses.KEY_LEFT and self.highlight[1] != 0:
                # move highlight to the left
                self.highlight[1] -= 1
                self.render()
            elif key == curses.KEY_RIGHT and self.highlight[1] != self.size - 1:
                # move highlight to the right
                self.highlight[1] += 1
                self.render()
            elif key == curses.KEY_UP and self.highlight[0] != 0:
                # move highlight up
                self.highlight[0] -= 1
                self.render()
            elif key == curses.KEY_DOWN and self.highlight[0] != self.size - 1:
                # move highlight down
                self.highlight[0] += 1
                self.render()
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if not self.can_place(self.highlight[0], self.highlight[1]):
                    continue

                # place a stone
                self.field[self.highlight[0]][self.highlight[1]] = self.player
                # Flip the stones
                for stone in self.check_flip(self.highlight[0], self.highlight[1]):
                    self.field[stone[0]][stone[1]] = self.player

                # toggle player
                self.player = 2 if self.player == 1 else 1
                self.render()
            self.stdscr.refresh()

    def can_place(self, x, y):
        # Check if the stone is already placed
        if self.field[x][y] is not None:
            return False
        # Check if there are stones to flip
        if len(self.check_flip(x, y)) == 0:
            return False

        return True

    def check_flip(self, x, y):
        total_stones_to_flip = []
        # Check if there are stones to flip
        # Check the 8 directions
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                total_stones_to_flip += self.check_direction(x, y, i, j)
        return total_stones_to_flip

    def check_direction(self, x, y, dx, dy):
        stones_to_flip = []

        # Check if there are stones to flip in a direction
        # If there are, append and return them
        # Check the direction (dx, dy)
        for i in range(1, self.size):
            check_x = x + i * dx
            check_y = y + i * dy
            # If the stone is out of the grid, return
            if check_x < 0 or check_x >= self.size or check_y < 0 or check_y >= self.size:
                return []
            # If the stone is empty, return
            if self.field[check_x][check_y] is None:
                return []
            # If the stone is the same color as the player, flip the stones
            elif self.field[check_x][check_y] == self.player:
                if i == 1:
                    return []
                # Flip the stones
                for j in range(1, i):
                    stones_to_flip.append([x + j * dx, y + j * dy])
                return stones_to_flip
        return []

    def check_end(self):
        player1 = 0
        player2 = 0
        for i in range(self.size):
            for j in range(self.size):
                # Check if there are still valid moves
                if self.can_place(i, j):
                    return False
                # Check if the field is full
                elif self.field[i][j] is None:
                    return False
                # Count the stones
                elif self.field[i][j] == 1:
                    player1 += 1
                else:
                    player2 += 1
        self.stdscr.addstr(4, 30, f'Player 1: {player1} stones')
        self.stdscr.addstr(8, 30, f'Player 2: {player2} stones')
        self.stdscr.addstr(16, 0, 'Press any key to exit...')
        return True

    def get_stats(self):
        player1 = 0
        player2 = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.field[i][j] == 1:
                    player1 += 1
                elif self.field[i][j] == 2:
                    player2 += 1

        return player1, player2


def main(stdscr):
    game = Reversi(10, stdscr)
    try:
        game.start_game()
    except KeyboardInterrupt:
        stats = game.get_stats()
        print('Final stats:')
        print(f'Player 1: {stats[0]} stones')
        print(f'Player 2: {stats[1]} stones')


wrapper(main)
