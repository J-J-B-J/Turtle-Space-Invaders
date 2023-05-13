"""A game of space invaderz"""
import json
import time
import turtle as t
from util import *
from importlib import reload
from random import randint, choice
from tkinter.messagebox import showwarning, showerror, askyesno
from tkinter import *
from json import load, dump, JSONDecodeError
from hashlib import sha256


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

        def __init__(self, x_pos, y_pos, speed=y(10), length=1, width=0.4,
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

    # class HighScore

    class Player:
        """A class to hold a player"""
        def __init__(self, name: str, password_en: bool, password_hash=None,
                     highscores: list[int] = []):
            self.name = name
            self.password_en = password_en
            self.password_hash = password_hash
            self.highscores = highscores

        def serialise(self):
            """Convert to a dictionary"""
            return {
                "name": self.name,
                "password_en": self.password_en,
                "password_hash": self.password_hash,
                "highscores": self.highscores
            }

    def playerfromdict(player_dict: dict):
        """Create a player from a dictionary"""
        try:
            return Player(
                name=player_dict["name"],
                password_en=player_dict["password_en"],
                password_hash=player_dict["password_hash"]
            )
        except KeyError:
            return None
        except ValeError:
            return None

    class Scorer:
        """A class to manage scoring"""
        def __init__(self, file_name):
            self.score = 0
            self.turtle = t.Turtle()
            self.turtle.hideturtle()
            self.turtle.penup()
            self.turtle.goto(pos(0, 350))
            self.turtle.color(255, 255, 255)
            self.file_name = file_name

            self.players = []
            self.load()
            self.player = None
            self.login()

            self.last_score_decrease = time.time()

        def login(self):
            """Login a player"""
            login_window = Tk()
            login_window.title("Login")
            login_window.geometry("200x300")

            logged_in = False

            # This section is largely based on and partly copied from my
            # fuzzy-parakeet repository, which is publicly available on GitHub.
            # https://github.com/J-J-B-J/fuzzy-parakeet/blob/b741830bbbb0acfa502ef0d6d87d1dcf1e9907dd/FuzzyParakeet.py#L42
            # I have not submitted this code in any other assessment task.
            player_label = Label(master=login_window, text="Username:")
            player_label.pack()
            player_list = Listbox(master=login_window, width=1)
            player_list.pack(side=TOP, fill=BOTH, expand=True)
            scrollbar = Scrollbar(master=player_list)
            scrollbar.pack(side=RIGHT, fill=BOTH)
            player_list.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=player_list.yview)

            for this_player in self.players:
                player_list.insert(END, this_player.name)

            def add_player():
                """Create a new player"""
                new_player_window = Tk()
                new_player_window.title("New Player")
                new_player_window.geometry("205x210")
                new_playername_label = Label(
                    master=new_player_window,
                    text="Username:"
                )
                new_playername_label.pack()
                new_playername_var = StringVar(master=new_player_window)
                new_playername_input = Entry(
                    master=new_player_window,
                    textvariable=new_playername_var
                )
                new_playername_input.pack()

                # Password Checkbox
                new_password_en_var = IntVar(master=new_player_window, value=1)
                new_password_en_check = Checkbutton(
                    master=new_player_window,
                    text="Password-Protected",
                    variable=new_password_en_var
                )
                new_password_en_check.pack()

                # Password Entry
                new_password_label = Label(
                    master=new_player_window,
                    text="Password:"
                )
                new_password_label.pack()
                new_password_var = StringVar(master=new_player_window)
                new_password_input = Entry(
                    master=new_player_window,
                    textvariable=new_password_var,
                    show="✱"
                )
                new_password_input.pack()

                # Password Verification
                new_password_verif_label = Label(
                    master=new_player_window,
                    text="Password again:"
                )
                new_password_verif_label.pack()
                new_password_verif_var = StringVar(master=new_player_window)
                new_password_verif_input = Entry(
                    master=new_player_window,
                    textvariable=new_password_verif_var,
                    show="✱"
                )
                new_password_verif_input.pack()

                def password_en_change(*_):
                    """Function to be called when password_en changes"""
                    if new_password_en_var.get():
                        new_password_input.config(state="normal")
                        new_password_label.config(state="normal")
                        new_password_verif_input.config(state="normal")
                        new_password_verif_label.config(state="normal")
                    else:
                        new_password_input.config(state="disabled")
                        new_password_label.config(state="disabled")
                        new_password_verif_input.config(state="disabled")
                        new_password_verif_label.config(state="disabled")
                        new_password_var.set("")
                        new_password_verif_var.set("")

                new_password_en_var.trace_add("write", password_en_change)

                def submit():
                    """Submit the form"""
                    new_playername = new_playername_var.get().strip()
                    new_password = new_password_var.get()
                    new_password_verif = new_password_verif_var.get()
                    if new_password != new_password_verif:
                        showerror(message="Passwords do not match!")
                        return
                    if new_playername == "":
                        showerror(message="Please enter a player name with at "
                                          "least one visible character.")
                        return
                    if new_playername in [p.name for p in self.players]:
                        showerror(message="That username is already in use!")
                        return
                    if new_password.strip() == "":
                        showerror(message="Please enter a password with at "
                                          "least one visible character.")
                        return

                    password_en = True if new_password_en_var.get() else False
                    if password_en:
                        password_hash = sha256(
                            new_password_input.get().encode()
                        ).hexdigest()
                    else:
                        password_hash = None
                    self.players.append(Player(
                        new_playername,
                        password_en,
                        password_hash
                    ))
                    new_player_window.destroy()
                    player_list.insert(END, new_playername)
                    self.save()

                submit_button = Button(master=new_player_window, text="Create",
                                       command=submit)
                submit_button.pack()

                while new_player_window:
                    new_player_window.update()

            def check_login(password: str) -> (bool, str or Player):
                """Check if credentials are correct"""
                if not player_list.curselection():
                    return False, "noSelect"
                logging_in_player = self.players[player_list.curselection()[0]]
                if sha256(password.encode()).hexdigest() == \
                        logging_in_player.password_hash or not \
                        logging_in_player.password_en:
                    return True, logging_in_player
                else:
                    return False, "wrongPassword"

            def login():
                """Login a player"""
                nonlocal logged_in
                success, result = check_login(password_var.get())
                if success:
                    self.player = result
                    logged_in = True
                elif result == "noSelect":
                    showerror(message="Please select a username!")
                    return
                else:
                    showerror(message="Incorrect username or password!")
                    return

            def guest_login():
                """Login as a guest"""
                nonlocal logged_in
                use_guest = askyesno(
                    message="Using a guest account will not save your scores."
                            "\nDo you want to continue as a guest?"
                )
                if use_guest:
                    self.player = "guest"
                    logged_in = True
                else:
                    return

            def delete_player():
                """Delete the selected account"""
                success, result = check_login(password_var.get())
                if success:
                    delete = askyesno(message=f"Are you sure you want to "
                                              f"delete '{result.name}'?")
                    if delete:
                        player_list.delete(self.players.index(result))
                        password_var.set("")
                        self.players.remove(result)
                        self.save()
                elif result == "noSelect":
                    showerror(message="Please select a username!")
                    return
                else:
                    showerror(message="Incorrect username or password!")
                    return

            password_label = Label(
                master=login_window,
                text="Password:"
            )
            password_label.pack()
            password_var = StringVar(master=login_window)
            password_input = Entry(
                master=login_window,
                textvariable=password_var,
                show="✱"
            )
            password_input.pack()

            frm_buttons_ = Frame(master=login_window)
            frm_buttons_.pack()
            btn_login = Button(
                master=frm_buttons_,
                text="Login",
                command=login
            )
            btn_login.pack(side=LEFT)
            btn_guest = Button(
                master=frm_buttons_,
                text="Guest",
                command=guest_login
            )
            btn_guest.pack(side=RIGHT)

            btn_new = Button(
                master=login_window,
                text="New Player...",
                command=add_player
            )
            btn_new.pack()
            btn_del = Button(
                master=login_window,
                text="Delete Player...",
                command=delete_player
            )
            btn_del.pack()

            while not logged_in:
                login_window.update()
            login_window.destroy()

        def serialise_players(self):
            """Serialise the players into json format."""
            return [this_player.serialise() for this_player in self.players]

        def load(self):
            """Load the scores from a file"""
            try:
                with open(self.file_name, "r") as scores_file:
                    players_data = load(scores_file)
                if type(players_data) != list:
                    raise TypeError
            except FileNotFoundError:
                showwarning(message="Unable to find high scores!\n"
                                    "Creating file...")
                self.save()
            except EOFError:
                showwarning(message="Unable to retrieve high scores!\n"
                                    "Resetting file...")
                self.save()
            except JSONDecodeError:
                showwarning(message="Unable to parse high scores!\n"
                                    "Resetting file...")
                self.save()
            except TypeError:
                showwarning(message="Unable to parse high scores!\n"
                                    "Resetting file...")
                self.save()
            else:
                for player_data in players_data:
                    player_obj = playerfromdict(player_data)
                    if player_obj is not None:
                        self.players.append(player_obj)

        def save(self):
            """Save the scores to a file"""
            try:
                with open(self.file_name, "w") as scores_file:
                    dump(self.serialise_players(), scores_file)
            except FileNotFoundError:
                showerror(message="Unable to save high scores!")

        def increase(self, amount: int):
            """Increase the score by an amount"""
            self.score += amount

        def decrease(self, amount: int):
            """Decrease the score by an amount"""
            self.score -= amount

        def draw_score(self):
            """Draw the score at the top of the screen."""
            # Update the score for the number of seconds
            if int(time.time() - self.last_score_decrease) >= 1:
                self.decrease(int(time.time() - self.last_score_decrease))
                self.last_score_decrease = time.time()

            # Draw the score
            self.turtle.clear()
            self.turtle.write(
                str(self.score),
                align="center",
                font=("Helvetica", int(y(50)), "normal")
            )

    scorer = Scorer("assets/scores/scores.json")

    class Ship:
        """A class to manage the player"""

        def __init__(self, y_pos, speed=8):
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
            nonlocal scorer
            if self.firing and self.time_last_bullet < time.time() - 0.5:
                bullets.append(Bullet(
                    self.turtle.xcor(),
                    self.turtle.ycor() + y(80),
                ))
                self.time_last_bullet = time.time()
                scorer.decrease(1)

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

        def __init__(self, x_pos, y_pos, level):
            self.turtle = t.Turtle()
            self.turtle.penup()
            self.turtle.goto(x_pos, y_pos)
            t.register_shape("assets/img/alien.gif")
            self.turtle.shape("assets/img/alien.gif")
            self.turtle.fillcolor((255, 255, 255))
            self.time_last_bullet = time.time() - 60
            self.level = level

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
            if randint(0, 1500 - (24 * (55 - alien_count))) == 0:
                if self.time_last_bullet < time.time() - 2:
                    bullets.append(Bullet(
                        self.turtle.xcor(),
                        self.turtle.ycor(),
                        y(-4),
                        fired_by_player=False
                    ))
                    self.time_last_bullet = time.time()

    player = Ship(y(-350))

    aliens = [Alien(x(x_pos), y(y_pos), 1) for x_pos in range(-550, 551, 110)
              for y_pos in range(0, 301, 75)]

    def end_screen(win: bool):
        """Show the end screen"""
        screen.clearscreen()
        screen.bgcolor(0, 0, 0)

        end_turtle = t.Turtle()
        end_turtle.hideturtle()
        end_turtle.penup()
        end_turtle.goto(pos(0, 0))
        end_turtle.color(1, 1, 1)
        if win:
            end_turtle.write(
                "Triumph!",
                align="center",
                font=("Helvetica", int(y(50)), "normal")
            )
        else:
            end_turtle.write(
                "Defeat!",
                align="center",
                font=("Helvetica", int(y(50)), "normal")
            )
        wait_ms(500, screen)
        end_turtle.goto(pos(0, -25))
        if win:
            end_turtle.write(
                choice([
                    "ethay ogurtfray isyay alsoyay ursedcay.",
                    "You sent the Romulans back in time with red matter!",
                    "Looks like you've won! Go drink a hot chocolate and watch"
                    " some TV or something.",
                    "Reward yourself with a 3D printed duck!",
                    "Tip: For a challenge, try destroying the aliens in the"
                    " middle first to speed them up.",
                ]),
                align="center",
                font=("Helvetica", int(y(20)), "normal")
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
                font=("Helvetica", int(y(20)), "normal")
            )
        wait_ms(1000, screen)
        end_turtle.goto(pos(0, -50))
        end_turtle.write(
                "Press Space to exit.",
                align="center",
                font=("Helvetica", int(y(15)), "normal")
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

        scorer.save()

        return

    last_frame_time = time.time_ns() / 1_000_000 - 10

    alien_direction = 1

    def alien_speed():
        """Get the alien speed"""
        return x(0.175 + (0.175 * (55 - len(aliens))))

    while True:
        current_time = time.time_ns() / 1_000_000
        time_diff = current_time - last_frame_time
        for _ in range(int(time_diff / 10)):
            if not aliens:
                end_screen(True)
                return

            player.move()

            alien_xs = [alien.turtle.xcor() for alien in aliens]
            max_alien_x = max(alien_xs)
            min_alien_x = min(alien_xs)

            alien_ys = [alien.turtle.ycor() for alien in aliens]
            min_alien_y = min(alien_ys)

            if min_alien_y < y(-240) or (not player.turtle.isvisible()):
                # Aliens have caught up, game ends
                end_screen(False)
                return

            if max_alien_x >= x(650):
                alien_direction = -1
                for alien in aliens:
                    alien.turtle.goto(
                        alien.turtle.xcor(),
                        alien.turtle.ycor() - y(10)
                    )
            elif min_alien_x <= x(-650):
                alien_direction = 1
                for alien in aliens:
                    alien.turtle.goto(
                        alien.turtle.xcor(),
                        alien.turtle.ycor() - y(10)
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
                    scorer.increase(10 * alien.level)
            for alien in aliens_to_delete:
                aliens.remove(alien)
                del alien

            bullets_to_delete = []
            for bullet in bullets:
                bullet.move(player, aliens)
                if bullet.turtle.ycor() < y(-500):
                    bullets_to_delete.append(bullet)
            for bullet in bullets_to_delete:
                bullet.turtle.hideturtle()
                bullets.remove(bullet)
                del bullet

        last_frame_time = time.time_ns() / 1_000_000
        scorer.draw_score()
        screen.update()


if __name__ == "__main__":
    run()
