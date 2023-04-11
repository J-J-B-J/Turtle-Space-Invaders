"""Naughts and crosses"""
import turtle as t
import random


# Get the screen
screen = t.getscreen()

# Disable animations
screen.tracer(0, 0)
# Make the colourmode 255
screen.colormode(255)
# Make the screen larger
screen.setup(width=1.0, height=1.0, startx=None, starty=None)
t.hideturtle()

# Optimise the screen size to make it the biggest ratio of 16:9 possible with
# the current window size (basically makes the game compatible with every
# screen size)
width = screen.window_width()
height = screen.window_height()
relative_width = width * 16
relative_height = height * 9


def coord(original_dimension: int, design_size: int, production_size: int):
    """Scale a coordinate to the correct size for the screen"""
    return int((original_dimension / design_size) * production_size)


if relative_width > relative_height:
    # The screen is slightly wider than 16:9, so the top and bottom edges will
    # be unused
    x = lambda num: coord(num, 1600, int((height/9)*16))
    y = lambda num: coord(num, 900, height)
elif relative_height > relative_width:
    # The screen is slightly taller than 16:9, so the left and right edges will
    # be unused
    x = lambda num: coord(num, 1600, width)
    y = lambda num: coord(num, 900, int((width/16)*9))
else:
    # The screen is exactly 16:9, so all edges will be exactly 16:9
    x = lambda num: coord(num, 1600, width)
    y = lambda num: coord(num, 900, height)

pos = lambda x_pos, y_pos: (x(x_pos), y(y_pos))


player_names = [
    t.textinput(f"Player {n} Name", f"Enter player {n} name:")
    for n in range(1, 3)
]


# Create the buttons
class Button:
    """A class for a button"""
    def __init__(self, x_coord: int, y_coord: int):
        self.x = x_coord
        self.y = y_coord
        self.state = 0  # 0 for empty, 1 for X, 2 for O
        self.turtle = t.Turtle()
        # Hide the turtle
        self.turtle.hideturtle()

    def draw(self) -> None:
        """Draw the button to the screen"""
        self.turtle.penup()
        self.turtle.end_fill()
        self.turtle.pensize(x(5))
        if self.state == 1:
            self.turtle.pencolor(20, 63, 107)
            self.turtle.goto(pos(self.x - 100, self.y - 100))
            self.turtle.pendown()
            self.turtle.goto(pos(self.x + 100, self.y + 100))
            self.turtle.penup()
            self.turtle.goto(pos(self.x + 100, self.y - 100))
            self.turtle.pendown()
            self.turtle.goto(pos(self.x - 100, self.y + 100))
            self.turtle.penup()
        elif self.state == 2:
            self.turtle.pencolor(245, 83, 83)
            self.turtle.goto(pos(self.x, self.y - 100))
            self.turtle.seth(0)
            self.turtle.pendown()
            self.turtle.circle(x(100), 360)
            self.turtle.penup()

    def set_state(self, state: int):
        """Set the state of the button and redraw the screen"""
        self.state = state
        self.turtle.clear()
        self.draw()
        t.update()

    def intersects_point(self, x_coord, y_coord) -> bool:
        """Check if the point intersects this button"""
        if abs(x_coord - self.x) < x(135) and abs(y_coord - self.y) < y(135):
            return True
        return False


button_grid = []

for y_pos in [-250, 0, 250]:
    row = []
    for x_pos in [-250, 0, 250]:
        row.append(Button(x(x_pos), y(y_pos)))
    button_grid.append(row)


grid_turtle = t.Turtle()
grid_turtle.hideturtle()


def draw_grid() -> None:
    """Draw the grid"""
    grid_turtle.penup()
    grid_turtle.end_fill()
    grid_turtle.pencolor(0, 0, 0)
    grid_turtle.pensize(x(5))
    for line_x in [-135, 135]:
        grid_turtle.goto(pos(line_x, -405))
        grid_turtle.pendown()
        grid_turtle.goto(pos(line_x, 405))
        grid_turtle.penup()
    for line_y in [-135, 135]:
        grid_turtle.goto(pos(-405, line_y))
        grid_turtle.pendown()
        grid_turtle.goto(pos(405, line_y))
        grid_turtle.penup()


player_turn = 1


def check_board():
    """Chech to see if there is a winner"""
    for button_row in button_grid:
        states = [button.state for button in button_row]
        if max(states) == min(states):
            return states[0]

    for col_num in range(3):
        states = [button_row[col_num].state for button_row in button_grid]
        if max(states) == min(states):
            return states[0]

    states = [button_grid[num][num].state for num in range(3)]
    if max(states) == min(states):
        return states[0]

    states = [button_grid[num][2-num].state for num in range(3)]
    if max(states) == min(states):
        return states[0]


def winner(winner_num: int):
    """There is a winner!"""
    winner_turtle = t.Turtle()
    winner_turtle.hideturtle()
    winner_turtle.penup()
    winner_turtle.fillcolor([(20, 63, 107), (245, 83, 83)][winner_num-1])
    winner_turtle.goto(pos(-800, 350))
    winner_turtle.begin_fill()
    winner_turtle.goto(pos(800, 350))
    winner_turtle.goto(pos(800, 250))
    winner_turtle.goto(pos(-800, 250))
    winner_turtle.end_fill()

    winner_turtle.goto(pos(0, 275))

    winner_turtle.color([(20, 63, 107), (245, 83, 83)][2-winner_num])
    winner_turtle.write(
        f"{player_names[winner_num-1]} wins!",
        align='center',
        font=('Helvetica', 50, 'normal')
    )


def handle_click(mouse_x, mouse_y) -> None:
    """Handle a mouse click"""
    global player_turn
    for grid_row in button_grid:
        for button in grid_row:
            if button.intersects_point(mouse_x, mouse_y) and button.state == 0:
                button.set_state(player_turn)
                player_turn = 1 if player_turn == 2 else 2
                winner_num = check_board()
                if winner_num != 0:
                    print(f"Player {winner_num} wins!")
                    winner(winner_num)
                    screen.onclick(None)
                return


draw_grid()
screen.onclick(handle_click)
screen.listen()
screen.update()
screen.mainloop()
