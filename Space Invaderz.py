"""A game of space invaderz"""
import time
import turtle as t
from util import *
from importlib import reload
from random import randint, choice


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

        def __init__(self, x_pos, y_pos, speed=15, length=1, width=0.4,
                     fired_by_player=True):
            self.speed = speed
            self.turtle = t.Turtle()
            self.turtle.penup()
            self.turtle.goto(x_pos, y_pos)
            self.turtle.shape("square")
            self.turtle.fillcolor((255, 255, 255))
            self.turtle.shapesize(length, width, 0)
            self.fired_by_player = fired_by_player

        def move(self, game_player=None, game_aliens=None):
            """Move the bullet"""
            if game_aliens is None:
                game_aliens = []

            if not self.turtle.isvisible():
                return

            self.turtle.goto(
                self.turtle.xcor(),
                self.turtle.ycor() + self.speed
            )

            if self.fired_by_player:
                for alien in game_aliens:
                    if alien.intersectspoint(
                            self.turtle.xcor(),
                            self.turtle.ycor()
                    ):
                        alien.turtle.hideturtle()
                        self.turtle.hideturtle()
            else:
                if game_player.intersectspoint(
                        self.turtle.xcor(),
                        self.turtle.ycor()
                ):
                    player.turtle.hideturtle()
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

        def move(self):
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
                    self.turtle.ycor() + y(80),
                ))
                self.time_last_bullet = time.time()

        def intersectspoint(self, x_pos, y_pos) -> bool:
            """Check if the player intersects a point"""
            tx = self.turtle.xcor()
            ty = self.turtle.ycor()
            # Check the fins
            if tx - 50 <= x_pos <= tx + 50 and ty - 35 <= y_pos <= ty - 15:
                self.turtle.hideturtle()
                return True
            # Check the passenger compartment
            if tx - 28 <= x_pos <= tx + 28 and ty - 15 <= y_pos <= ty + 60:
                self.turtle.hideturtle()
                return True
            # Check the nose
            if 2 * (x_pos - tx) + (y_pos - ty) < 105 and -2 * (x_pos - tx) + (
                    y_pos - ty) < 105 and y_pos - ty > 50:
                self.turtle.hideturtle()
                return True
            return False

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
            if self.turtle.xcor() - 50 <= x_pos <= self.turtle.xcor() + 50 \
                    and self.turtle.ycor() - 27 <= y_pos <= self.turtle.ycor():
                self.turtle.hideturtle()
                return True
            else:
                return False

        def generate_bullet(self, alien_count):
            """Fire a bullet"""
            if randint(0, 1500 - (10 * (55 - alien_count))) == 0:
                if self.time_last_bullet < time.time() - 2:
                    bullets.append(Bullet(
                        self.turtle.xcor(),
                        self.turtle.ycor(),
                        -5,
                        fired_by_player=False
                    ))
                    self.time_last_bullet = time.time()

    player = Player(y(-350))

    aliens = [Alien(x(x_pos), y(y_pos)) for x_pos in range(-550, 551, 110)
              for y_pos in range(100, 401, 75)]

    def end_screen(win: bool):
        """Show the end screen"""
        screen.clearscreen()
        screen.bgcolor(0, 0, 0)

        end_turtle = t.Turtle()
        end_turtle.hideturtle()
        end_turtle.penup()
        end_turtle.goto(0, 0)
        end_turtle.color(1, 1, 1)
        if win:
            end_turtle.write(
                "You Win!",
                align="center",
                font=("Helvetica", 50, "normal")
            )
        else:
            end_turtle.write(
                "You Lose!",
                align="center",
                font=("Helvetica", 50, "normal")
            )
        wait_ms(500, screen)
        end_turtle.goto(0, -25)
        if win:
            end_turtle.write(
                choice([
                    "ethay ogurtfray isyay alsoyay ursedcay.",
                    "You sent the Romulans back in time with red matter!",
                    "Looks like you've won! Go drink a hot chocolate and watch"
                    " some TV or something.",
                    "Reward yourself with a 3D printed Blue or Gold duck from"
                    " Ethan Phillips for only 50¢!",
                    "Tip: For a challenge, try destroying the aliens in the"
                    " middle first to speed them up.",
                ]),
                align="center",
                font=("Helvetica", 20, "normal")
            )
        else:
            end_turtle.write(
                choice([
                    "Better luck next time!",
                    "You were attacked by Romulans!",
                    "You'd better play again!",
                    "Practice makes perfect!",
                    "Tip: Try destroying the aliens on the edge first to slow"
                    " them down.",
                ]),
                align="center",
                font=("Helvetica", 20, "normal")
            )
        wait_ms(1000, screen)
        end_turtle.goto(0, -50)
        end_turtle.write(
                "Press Space to exit.",
                align="center",
                font=("Helvetica", 15  , "normal")
            )

        done = False

        def finish():
            """Set done to true"""
            nonlocal done
            done = True

        screen.onkeypress(finish, "space")
        screen.listen()

        while not done:
            screen.update()

        return

    last_frame_time = time.time_ns() / 1_000_000 - 10

    alien_direction = 1

    def alien_speed():
        """Get the alien speed"""
        return 0.1 + (0.15 * (55 - len(aliens)))

    while True:
        if not aliens:
            print("You WIN!")
            end_screen(True)
            return

        current_time = time.time_ns() / 1_000_000
        time_diff = current_time - last_frame_time
        for _ in range(int(time_diff / 10)):
            player.move()

            alien_xs = [alien.turtle.xcor() for alien in aliens]
            max_alien_x = max(alien_xs)
            min_alien_x = min(alien_xs)

            alien_ys = [alien.turtle.ycor() for alien in aliens]
            min_alien_y = min(alien_ys)

            if min_alien_y < y(-240) or (not player.turtle.isvisible()):
                # Aliens have caught up, game ends
                print("Game Over!")
                end_screen(False)
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
                del alien

            bullets_to_delete = []
            for bullet in bullets:
                bullet.move(player, aliens)
                if bullet.turtle.ycor() < -500:
                    bullets_to_delete.append(bullet)
            for bullet in bullets_to_delete:
                bullets.remove(bullet)
                del bullet

        last_frame_time = time.time_ns() / 1_000_000
        screen.update()


if __name__ == "__main__":
    run()
