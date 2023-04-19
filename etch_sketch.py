"""Etch a sketch game"""
import time
import turtle as t
import tkinter as tk
from util import optimised_coord_funcs
from importlib import reload


SPEED = 5


def run():
    """Run the game"""
    reload(t)
    # Get the screen
    screen = t.Screen()

    # Disable animations
    # screen.tracer(0, 0)
    # Make the colourmode 255
    screen.colormode(255)
    # Make the screen larger
    screen.setup(width=1.0, height=1.0, startx=None, starty=None)
    # t.hideturtle()
    screen.update()
    screen.title("Etch a Sketch")

    etch_turtle = t.Turtle()
    etch_turtle.hideturtle()
    etch_turtle.width(3)
    etch_turtle.pendown()

    pressed_keys = []
    screen.onkeypress(lambda *_: pressed_keys.append("w"), "w")
    screen.onkeyrelease(lambda *_: pressed_keys.remove("w"), "w")
    screen.onkeypress(lambda *_: pressed_keys.append("s"), "s")
    screen.onkeyrelease(lambda *_: pressed_keys.remove("s"), "s")
    screen.onkeypress(lambda *_: pressed_keys.append("a"), "a")
    screen.onkeyrelease(lambda *_: pressed_keys.remove("a"), "a")
    screen.onkeypress(lambda *_: pressed_keys.append("d"), "d")
    screen.onkeyrelease(lambda *_: pressed_keys.remove("d"), "d")
    screen.onkeypress(etch_turtle.clear, "p")

    def moveturtle():
        """Move the turtle according to the pressed keys"""
        new_coord = [etch_turtle.xcor(), etch_turtle.ycor()]
        if "w" in pressed_keys and "s" not in pressed_keys:
            new_coord[1] += SPEED
        elif "w" not in pressed_keys and "s" in pressed_keys:
            new_coord[1] -= SPEED
        if "a" in pressed_keys and "d" not in pressed_keys:
            new_coord[0] -= SPEED
        elif "a" not in pressed_keys and "d" in pressed_keys:
            new_coord[0] += SPEED
        etch_turtle.goto(tuple(new_coord))
        screen.ontimer(moveturtle, 20)

    screen.ontimer(moveturtle, 20)
    screen.listen()
    screen.mainloop()


if __name__ == "__main__":
    run()
