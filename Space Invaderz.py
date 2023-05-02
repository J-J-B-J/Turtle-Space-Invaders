"""A game of space invaderz"""
import time
import turtle as t
from util import optimised_coord_funcs
from importlib import reload
from random import randint


def run():
    """Run the game"""
    reload(t)
    # Get the screen
    screen = t.getscreen()

    # Disable animations
    screen.tracer(0, 0)
    # Make the colourmode 255
    screen.colormode(255)
    # Make the screen larger
    screen.setup(width=1.0, height=1.0, startx=None, starty=None)
    t.hideturtle()
    screen.update()
    screen.title("Space Invaderz")
    screen.bgcolor((0, 0, 0))

    x, y, pos = optimised_coord_funcs(
        screen.window_width(), screen.window_height(),
        1300, 900
    )

    class Bullet:
        """A class to manage a bullet"""
        def __init__(self, x_pos, y_pos, speed=15, length=1, width=0.4):
            self.speed = speed
            self.turtle = t.Turtle()
            self.turtle.penup()
            self.turtle.goto(x_pos, y_pos)
            self.turtle.shape("square")
            self.turtle.fillcolor((255, 255, 255))
            self.turtle.shapesize(length, width, 0)

        def move(self, aliens=None):
            """Move the bullet"""
            if aliens is None:
                aliens = []

            if not self.turtle.isvisible():
                return

            self.turtle.goto(
                self.turtle.xcor(),
                self.turtle.ycor() + self.speed
            )

            for alien in aliens:
                if alien.intersectspoint(
                        self.turtle.xcor(),
                        self.turtle.ycor()
                ):
                    alien.turtle.hideturtle()
                    self.turtle.hideturtle()

    bullets = []

    class Player:
        """A class to manage the player"""

        def __init__(self, y_pos, speed=10):
            self.speed = speed
            self.movement = 0
            self.turtle = t.Turtle()
            self.turtle.penup()
            self.turtle.goto(0, y_pos)
            t.register_shape("assets/img/ship.gif")
            self.turtle.shape("assets/img/ship.gif")
            self.activate_controls()
            self.firing = False
            self.time_last_bullet = time.time() - 60

        def move(self, aliens):
            """Move"""
            self.generate_bullet()

            if self.turtle.xcor() + (self.movement * self.speed) < x(-650):
                self.turtle.goto(x(-650), self.turtle.ycor())
            elif self.turtle.xcor() + (self.movement * self.speed) > x(650):
                self.turtle.goto(x(650), self.turtle.ycor())
            else:
                self.turtle.goto(
                    self.turtle.xcor() + (self.movement * self.speed),
                    self.turtle.ycor()
                )

        def beg_left(self):
            """Start moving left"""
            if self.movement == 0:
                self.movement = -1
            else:
                self.movement = 0

        def beg_right(self):
            """Start moving right"""
            if self.movement == 0:
                self.movement = 1
            else:
                self.movement = 0

        def end_left(self):
            """Stop moving left"""
            if self.movement == 0:
                self.movement = 1
            else:
                self.movement = 0

        def end_right(self):
            """Stop moving right"""
            if self.movement == 0:
                self.movement = -1
            else:
                self.movement = 0

        def beg_fire(self):
            """Start firing"""
            self.firing = True

        def end_fire(self):
            """Stop firing"""
            self.firing = False

        def activate_controls(self):
            """Activate the controls."""
            screen.onkeypress(self.beg_left, "Left")
            screen.onkeypress(self.beg_right, "Right")
            screen.onkeyrelease(self.end_left, "Left")
            screen.onkeyrelease(self.end_right, "Right")
            screen.onkeypress(self.beg_fire, "space")
            screen.onkeyrelease(self.end_fire, "space")
            screen.listen()

        def deactivate_controls(self):
            """Deactivate the controls."""
            screen.onkeypress(lambda: None, "Left")
            screen.onkeypress(lambda: None, "Right")
            screen.onkeyrelease(lambda: None, "Left")
            screen.onkeyrelease(lambda: None, "Right")
            screen.onkeypress(lambda: None, "space")
            screen.onkeyrelease(lambda: None, "space")
            screen.listen()

        def generate_bullet(self):
            """Fire a bullet"""
            if self.firing and self.time_last_bullet < time.time() - 0.5:
                bullets.append(Bullet(
                    self.turtle.xcor(),
                    self.turtle.ycor() + y(80)
                ))
                self.time_last_bullet = time.time()

    class Alien:
        """A class to manage an Alien ship"""
        def __init__(self, x_pos, y_pos):
            self.turtle = t.Turtle()
            self.turtle.penup()
            self.turtle.goto(x_pos, y_pos)
            t.register_shape("assets/img/alien.gif")
            self.turtle.shape("assets/img/alien.gif")
            self.turtle.fillcolor((255, 255, 255))
            self.turtle.shapesize(1, 0.4, 0)
            self.time_last_bullet = time.time() - 60

        def intersectspoint(self, x_pos, y_pos) -> bool:
            """Check if the alien intersects a point"""
            if self.turtle.xcor() - 50 <= x_pos <= self.turtle.xcor() + 50 and\
                    self.turtle.ycor() - 27 <= y_pos <= self.turtle.ycor():
                self.turtle.hideturtle()
                return True
            else:
                return False

        def generate_bullet(self, alien_count):
            """Fire a bullet"""
            if randint(0, 1500 - (10*(55-alien_count))) == 0:
                if self.time_last_bullet < time.time() - 2:
                    bullets.append(Bullet(
                        self.turtle.xcor(),
                        self.turtle.ycor(),
                        -5
                    ))
                    self.time_last_bullet = time.time()

    player = Player(y(-350))

    aliens = [Alien(x(x_pos), y(y_pos)) for x_pos in range(-550, 551, 110)
              for y_pos in range(100, 401, 75)]

    last_frame_time = time.time_ns()/1_000_000 - 10

    alien_direction = 1

    def alien_speed():
        """Get the alien speed"""
        return 0.1 + (0.15 * (55-len(aliens)))

    while True:
        if not aliens:
            print("You WIN!")
            return

        current_time = time.time_ns()/1_000_000
        time_diff = current_time - last_frame_time
        for _ in range(int(time_diff/10)):
            player.move(aliens)

            alien_xs = [alien.turtle.xcor() for alien in aliens]
            max_alien_x = max(alien_xs)
            min_alien_x = min(alien_xs)

            alien_ys = [alien.turtle.ycor() for alien in aliens]
            min_alien_y = min(alien_ys)

            if min(alien_ys) < y(-240):
                # Aliens have caught up, game ends
                print("Game Over!")
                return

            if max_alien_x >= 650:
                alien_direction = -1
                for alien in aliens:
                    alien.turtle.goto(
                        alien.turtle.xcor(),
                        alien.turtle.ycor() - 10
                    )
            elif min_alien_x <= -650:
                alien_direction = 1
                for alien in aliens:
                    alien.turtle.goto(
                        alien.turtle.xcor(),
                        alien.turtle.ycor() - 10
                    )

            aliens_to_delete = []
            for alien in aliens:
                if alien.turtle.isvisible():
                    alien.turtle.goto(
                        alien.turtle.xcor()
                        + (alien_speed() * alien_direction),
                        alien.turtle.ycor()
                    )
                    alien_bottom_of_column = True
                    for alien_2 in aliens:
                        if alien_2.turtle.xcor() == alien.turtle.xcor() and \
                                    alien_2.turtle.ycor() < alien.turtle.ycor():
                            alien_bottom_of_column = False
                            break

                    if alien_bottom_of_column:
                        alien.generate_bullet(len(aliens))
                else:
                    aliens_to_delete.append(alien)
            for alien in aliens_to_delete:
                aliens.remove(alien)

            for bullet in bullets:
                bullet.move()

        last_frame_time = time.time_ns()/1_000_000
        screen.update()


if __name__ == "__main__":
    run()
