"""Guess the numebr"""
import random
import turtle as t
import tkinter.messagebox as mb
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
    # t.hideturtle()
    screen.update()
    screen.title("Guess the number")
    screen.bgcolor(20, 20, 20)

    x, y, pos = optimised_coord_funcs(
        screen.window_width(), screen.window_height(),
        1000, 1000
    )

    number_to_guess = random.randint(0, 99)
    guesses = 0

    current_text = ""

    guess_turtle = t.Turtle()
    guess_turtle.hideturtle()
    guess_turtle.penup()

    def add_ct(num):
        """Add a number to the current text"""
        nonlocal current_text
        if len(current_text) >= 2:
            return
        current_text += str(num)
        guess_turtle.clear()
        guess_turtle.color(255, 255, 255)
        guess_turtle.write(
            current_text,
            align="center",
            font=(
                "Helvetica",
                100,
                ""
            )
        )

    def rem_ct():
        """Remove the last entered letter"""
        nonlocal current_text
        current_text = current_text[:-1]
        guess_turtle.clear()
        guess_turtle.color(255, 255, 255)
        guess_turtle.write(
            current_text,
            align="center",
            font=(
                "Helvetica",
                100,
                ""
            )
        )

    screen.onkeypress(lambda: add_ct("0"), "0")
    screen.onkeypress(lambda: add_ct("1"), "1")
    screen.onkeypress(lambda: add_ct("2"), "2")
    screen.onkeypress(lambda: add_ct("3"), "3")
    screen.onkeypress(lambda: add_ct("4"), "4")
    screen.onkeypress(lambda: add_ct("5"), "5")
    screen.onkeypress(lambda: add_ct("6"), "6")
    screen.onkeypress(lambda: add_ct("7"), "7")
    screen.onkeypress(lambda: add_ct("8"), "8")
    screen.onkeypress(lambda: add_ct("9"), "9")
    screen.onkeypress(rem_ct, "BackSpace")

    def handle_guess():
        """Handle the user taking a guess"""
        nonlocal guesses, current_text
        guesses += 1

        guess = int(current_text)
        if guess == number_to_guess:
            mb.showinfo(message=f"You cracked it in {guesses} guesses!")
            screen.exitonclick()
            try:
                while True:
                    screen.update()
            except t.Terminator:
                return
        elif guess < number_to_guess:
            mb.showinfo(message=f"The number is higher than {guess}.")
        else:
            mb.showinfo(message=f"The number is lower than {guess}.")
        current_text = ""
        guess_turtle.clear()
        screen.listen()

    screen.onkeypress(handle_guess, "Return")
    screen.listen()
    screen.mainloop()


if __name__ == "__main__":
    run()
