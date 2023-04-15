"""Naughts and crosses"""
import time
import turtle as t
import tkinter as tk
from util import optimised_coord_funcs
from importlib import reload


def run():
    """Run the game"""
    reload(t)
    # Get the screen
    screen = t.Screen()

    # Disable animations
    screen.tracer(0, 0)
    # Make the colourmode 255
    screen.colormode(255)
    # Make the screen larger
    screen.setup(width=1.0, height=1.0, startx=None, starty=None)
    screen.update()
    screen.title("Tic Tac Toe")

    x, y, pos = optimised_coord_funcs(
        screen.window_width(), screen.window_height(),
        1600, 900
    )

    setup_window = tk.Tk()
    setup_window.title("Tic Tac Toe")
    setup_window.geometry("200x220")
    setup_window.resizable(False, False)

    p1_var = tk.StringVar(setup_window, "Player 1")
    p2_var = tk.StringVar(setup_window, "Player 2")

    p1_entry = tk.Entry(setup_window, textvariable=p1_var)
    p2_entry = tk.Entry(setup_window, textvariable=p2_var)

    tk.Label(setup_window, text="Player 1 Name").pack()
    p1_entry.pack()
    tk.Label(setup_window, text="Player 2 Name").pack()
    p2_entry.pack()

    done = False

    def start(*_):
        """Start the game"""
        nonlocal done
        done = True

    round_count_var = tk.StringVar(setup_window, "1")
    error_var = tk.StringVar(setup_window, "\n")

    submit_btn = tk.Button(setup_window, text="START")
    submit_btn.bind("<Button-1>", start)

    def check_round_count_var(*_):
        """Check that round_var is valid."""
        nonlocal error_var
        round_count = round_count_var.get()
        try:
            if int(round_count) < 1 or int(round_count) % 2 == 0:
                raise ValueError
        except ValueError:
            error_var.set("Please enter a positive integer\n that is not"
                          " divisible by 2!")
            submit_btn.unbind("<Button-1>")
            submit_btn.config(state="disabled")
        else:
            error_var.set('\n')
            submit_btn.bind("<Button-1>", start)
            submit_btn.config(state="normal")

    round_count_var.trace_add("write", callback=check_round_count_var)
    round_count_entry = tk.Entry(setup_window, textvariable=round_count_var)
    tk.Label(setup_window, text="Best of...").pack()
    round_count_entry.pack()

    error_label = tk.Label(setup_window, textvariable=error_var)
    submit_btn.pack()
    error_label.pack()

    while not done:
        setup_window.update()

    setup_window.destroy()
    del setup_window

    player_names = [p1_var.get(), p2_var.get()]
    rounds_to_play = int(round_count_var.get())

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

        def set_state(self, state: int, update: bool = True):
            """Set the state of the button and redraw the screen"""
            self.state = state
            self.turtle.clear()
            self.draw()
            if update:
                screen.update()

        def intersects_point(self, x_coord, y_coord) -> bool:
            """Check if the point intersects this button"""
            if abs(x_coord - self.x) < x(135) and abs(y_coord - self.y) < y(
                    135):
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

    starting_player = 1
    player_turn = 1

    def check_board():
        """Chech to see if there is a winner"""
        for button_row in button_grid:
            states = [button.state for button in button_row]
            if max(states) == min(states) and states[0] > 0:
                return states[0]

        for col_num in range(3):
            states = [button_row[col_num].state for button_row in button_grid]
            if max(states) == min(states) and states[0] > 0:
                return states[0]

        states = [button_grid[num][num].state for num in range(3)]
        if max(states) == min(states) and states[0] > 0:
            return states[0]

        states = [button_grid[num][2 - num].state for num in range(3)]
        if max(states) == min(states) and states[0] > 0:
            return states[0]

        return 0

    rounds_so_far = 0
    draw_grid()
    screen.update()

    scores = [0, 0]

    score_turtle_1 = t.Turtle()
    score_turtle_1.hideturtle()
    score_turtle_2 = t.Turtle()
    score_turtle_2.hideturtle()

    def draw_scores(winner_num):
        """Draw the scores to the screen"""
        if winner_num == 1:
            score_turtle_1.clear()
            score_turtle_1.penup()
            score_turtle_1.goto(pos(-600, -100))
            score_turtle_1.color((20, 63, 107))
            score_turtle_1.write(
                scores[0],
                align="center",
                font=(
                    "Helvetica",
                    int(500 / len(str(scores[0]))),
                    ""
                )
            )
        else:
            score_turtle_2.clear()
            score_turtle_2.penup()
            score_turtle_2.goto(pos(600, -100))
            score_turtle_2.color((245, 83, 83))
            score_turtle_2.write(
                scores[1],
                align="center",
                font=(
                    "Helvetica",
                    int(500 / len(str(scores[1]))),
                    ""
                )
            )

    draw_scores(1)
    draw_scores(2)

    def winner(winner_num: int):
        """There is a winner!"""
        nonlocal rounds_so_far, starting_player, player_turn

        rounds_so_far += 1
        scores[winner_num - 1] += 1

        draw_scores(winner_num)

        winner_turtle = t.Turtle()
        winner_turtle.hideturtle()
        winner_turtle.penup()
        winner_turtle.fillcolor([(20, 63, 107), (245, 83, 83)][winner_num - 1])
        winner_turtle.goto(pos(-800, 350))
        winner_turtle.begin_fill()
        winner_turtle.goto(pos(800, 350))
        winner_turtle.goto(pos(800, 250))
        winner_turtle.goto(pos(-800, 250))
        winner_turtle.end_fill()

        winner_turtle.goto(pos(0, 275))

        winner_turtle.color([(20, 63, 107), (245, 83, 83)][2 - winner_num])
        winner_turtle.write(
            f"{player_names[winner_num - 1]} wins!",
            align='center',
            font=('Helvetica', 50, 'normal')
        )

        start_time = time.time()
        while time.time() < start_time + 3:
            screen.update()

        winner_turtle.clear()

        if rounds_so_far >= rounds_to_play:
            screen.exitonclick()
            try:
                while True:
                    screen.update()
            except screen.Terminator:
                return
        else:
            for row in button_grid:
                for button in row:
                    button.set_state(0, False)

            starting_player = 1 if starting_player == 2 else 2
            player_turn = starting_player

            screen.onclick(handle_click)
            screen.listen()

    def handle_click(mouse_x, mouse_y) -> None:
        """Handle a mouse click"""
        nonlocal player_turn
        for grid_row in button_grid:
            for button in grid_row:
                if button.intersects_point(mouse_x,
                                           mouse_y) and button.state == 0:
                    button.set_state(player_turn)
                    player_turn = 1 if player_turn == 2 else 2
                    winner_num = check_board()
                    if winner_num > 0:
                        screen.onclick(lambda *_: None)
                        winner(winner_num)
                    return

    for button_row in button_grid:
        for button in button_row:
            button.set_state(0, False)
    screen.onclick(handle_click)
    screen.listen()
    screen.mainloop()


if __name__ == "__main__":
    run()
