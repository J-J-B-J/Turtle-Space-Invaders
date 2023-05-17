"""A game of space invaderz"""
#  Copyright (c) 2023 Joshua Lea. Some Rights Reserved.

import json
import time
import turtle as t
from util import *
from random import randint, choice
from tkinter.messagebox import showwarning, showerror, askyesno
from tkinter import *
from json import load, dump, JSONDecodeError
from hashlib import sha256
from sys import exit

# Get the screen
screen = t.getscreen()

screen.tracer(0, 0)  # Disable animations
screen.colormode(255)  # Make the colourmode 255
# Make the screen larger
screen.setup(width=1.0, height=1.0, startx=None, starty=None)
t.hideturtle()  # Hide the default turtle
screen.update()  # Update the screen initially
screen.title("Space Invaderz")  # Give the window a name
screen.bgcolor((0, 0, 0))  # Set the background colour to black

# Create the coordinate optimisation functions
x, y, pos = optimised_coord_funcs(
    screen.window_width(), screen.window_height(),
    1420, 900
)

# Draw a border on the screen
border_turtle = t.Turtle()
border_turtle.penup()
border_turtle.hideturtle()
border_turtle.pencolor(255, 255, 255)
border_turtle.pensize(5)
# Draw the border
border_turtle.goto(pos(-710, -450))
border_turtle.pendown()
border_turtle.goto(pos(710, -450))
border_turtle.goto(pos(710, 450))
border_turtle.goto(pos(-710, 450))
border_turtle.goto(pos(-710, -450))
border_turtle.penup()


class Bullet:
    """A class to manage a bullet"""

    def __init__(self, x_pos, y_pos, speed=y(10), length=y(1),
                 width=x(0.4), fired_by_player=True, color=(230, 84, 45)):
        self.speed = speed
        self.turtle = t.Turtle()  # Create a turtle to act as the bullet
        # Move the turtle to the right position and make it look right
        self.turtle.penup()
        self.turtle.goto(x_pos, y_pos)
        self.turtle.shape("square")
        self.turtle.fillcolor(color)
        self.turtle.shapesize(length, width, 0)
        # Was this bullet fired by the player or an alien?
        self.fired_by_player = fired_by_player

    def move(self, game_player=None, game_aliens=None):
        """Move the bullet"""
        # If the game_aliens parameter is empty, set it to an empty list
        if game_aliens is None:
            game_aliens = []

        # If the turtle is invisible (if the bullet has been used), then
        # exit the function
        if not self.turtle.isvisible():
            return

        # Move the bullet according to its speed
        self.turtle.goto(
            self.turtle.xcor(),
            self.turtle.ycor() + self.speed
        )

        if self.fired_by_player:  # If the bullet was fired by a player
            # Check to see if the bullet has hit an alien
            for alien in game_aliens:
                if alien.intersectspoint(
                        self.turtle.xcor(),
                        self.turtle.ycor()
                ):
                    # If it has, destroy the alien and the bullet, then
                    # exit this function
                    alien.dead()
                    self.turtle.hideturtle()
                    break
        else:  # If the bullet was fired by an alien
            # If the bullet has hit the player
            if game_player.intersectspoint(
                    self.turtle.xcor(),
                    self.turtle.ycor()
            ):
                # Destroy the player and the bullet
                player.dead()
                self.turtle.hideturtle()


# Create a list to store the bullets
bullets = []


class Player:
    """A class to hold a player"""

    def __init__(self, name: str, password_en: bool, password_hash=None,
                 highscore=0):
        self.name = name  # Player name
        self.password_en = password_en  # Password is enabled?
        self.password_hash = password_hash  # Hash of the password (if any)
        self.highscore = highscore  # The player's highscore

    def serialise(self):
        """Convert to a dictionary"""
        return {
            "name":          self.name,
            "password_en":   self.password_en,
            "password_hash": self.password_hash,
            "highscore":     self.highscore
        }


def playerfromdict(player_dict: dict):
    """Create a player from a dictionary"""
    try:
        return Player(
            name=player_dict["name"],  # Player name
            password_en=player_dict["password_en"],  # Password is enabled
            password_hash=player_dict["password_hash"],  # Hash of password
            highscore=player_dict["highscore"]  # Player highscore
        )
    except KeyError:
        return None  # Error, return nothing
    except ValueError:
        return None  # Error, return nothing


class Scorer:
    """A class to manage scoring"""

    def __init__(self, file_name):
        self.score = 0  # Game score
        # Create a turtle to write the score to the screen
        self.turtle = t.Turtle()
        # Make the turtle look right and move it into the right position
        self.turtle.hideturtle()
        self.turtle.penup()
        self.turtle.goto(pos(0, 350))
        self.turtle.color(255, 255, 255)
        # The .json file name containing the scores
        self.file_name = file_name

        self.players = []  # Store a list of all players
        self.load()  # Load the players and highscores
        self.player = None  # Store the currently logged in player
        self.login()  # Login a player

        # Store the last time the score was decreased (needed because you
        # lose a point for every second you take)
        self.last_score_decrease = time.time()

    def game_over(self):
        """Function to be called when the game ends, to save the scores"""
        if self.players:  # If there is at least one player created
            alltime_high = max([a.highscore for a in self.players])
        else:  # If there are no players
            alltime_high = 0  # No high score

        if self.score > alltime_high:
            high = 2  # Alltime highscore
        elif self.player == "guest":  # If the player isn't logged in
            high = 0  # No highscore
        elif self.score > self.player.highscore:  # If it's a personal best
            high = 1  # Personal best
        else:
            high = 0

        if high > 0 and self.player != "guest":
            self.player.highscore = self.score  # Set the new high score
            self.save()  # Save the data
        return high  # Return the high status

    def login(self):
        """Login a player"""
        login_window = Tk()  # Create a tkinter window to log in
        login_window.title("Login")  # Give the window a name
        login_window.geometry("200x300")  # Set the window size

        # Create a variable to determine if the player has logged in yet
        logged_in = False

        # This section is largely based on and partly copied from my
        # fuzzy-parakeet repository, which is publicly available on GitHub.
        # https://github.com/J-J-B-J/fuzzy-parakeet/blob
        # /b741830bbbb0acfa502ef0d6d87d1dcf1e9907dd/FuzzyParakeet.py#L42
        # I have not submitted this code in any other assessment task.

        # Create a label to say "Username:"
        player_label = Label(master=login_window, text="Username:")
        player_label.pack()

        # Create a list of all the usernames
        player_list = Listbox(master=login_window, width=1)
        player_list.pack(side=TOP, fill=BOTH, expand=True)
        # Create a scrollbar for the list
        scrollbar = Scrollbar(master=player_list)
        scrollbar.pack(side=RIGHT, fill=BOTH)
        # Bind the scrollbar to the listbox
        player_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=player_list.yview)
        # Add all the players to the list
        for this_player in self.players:
            player_list.insert(END, this_player.name)

        def add_player():
            """Callback for creating a new player"""
            # Create a window for creating a player
            new_player_window = Tk()
            new_player_window.title("New Player")  # Give the window a name
            new_player_window.geometry("205x210")  # Set the window size

            # Create a label that says "Username:"
            new_playername_label = Label(
                master=new_player_window,
                text="Username:"
            )
            new_playername_label.pack()

            # Create a StringVar and an entry widget to get the username
            new_playername_var = StringVar(master=new_player_window)
            new_playername_input = Entry(
                master=new_player_window,
                textvariable=new_playername_var
            )
            new_playername_input.pack()

            # Create a labelled checkbox to ask if the account is password
            # protected
            new_password_en_var = IntVar(master=new_player_window, value=1)
            new_password_en_check = Checkbutton(
                master=new_player_window,
                text="Password-Protected",
                variable=new_password_en_var
            )
            new_password_en_check.pack()

            # Create a label saying "Password:"
            new_password_label = Label(
                master=new_player_window,
                text="Password:"
            )
            new_password_label.pack()
            # Create a StringVar and an entry widget to get the password
            new_password_var = StringVar(master=new_player_window)
            new_password_input = Entry(
                master=new_player_window,
                textvariable=new_password_var,
                show="✱"
            )
            new_password_input.pack()

            # # Create a label saying "Password again:"
            new_password_verif_label = Label(
                master=new_player_window,
                text="Password again:"
            )
            new_password_verif_label.pack()
            # Create a StringVar and an entry widget to verify the password
            new_password_verif_var = StringVar(master=new_player_window)
            new_password_verif_input = Entry(
                master=new_player_window,
                textvariable=new_password_verif_var,
                show="✱"
            )
            new_password_verif_input.pack()

            def password_en_change(*_):
                """Callback for when password_en_var changes"""
                # If the password is enabled
                if new_password_en_var.get():
                    # Enable all the inputs for the password and password
                    # verification
                    new_password_input.config(state="normal")
                    new_password_label.config(state="normal")
                    new_password_verif_input.config(state="normal")
                    new_password_verif_label.config(state="normal")
                else:
                    # Disable all the inputs for the password and password
                    # verification
                    new_password_input.config(state="disabled")
                    new_password_label.config(state="disabled")
                    new_password_verif_input.config(state="disabled")
                    new_password_verif_label.config(state="disabled")
                    # Empty the entries
                    new_password_var.set("")
                    new_password_verif_var.set("")

            # Bind the password_en_change function to when password_en is
            # changed
            new_password_en_var.trace_add("write", password_en_change)

            def submit():
                """Callback for when the submit button is pressed"""
                # Get the player name, password, password verification and
                # wether or not the password was enabled
                new_playername = new_playername_var.get().strip()
                new_password = new_password_var.get()
                new_password_verif = new_password_verif_var.get()
                password_en = True if new_password_en_var.get() else False

                # If the password does not match the password verificarion
                if new_password != new_password_verif:
                    # Tell the user that the passwords don't match and
                    # cancel the submission
                    showerror(message="Passwords do not match!")
                    return
                # if a name was not entered
                if new_playername == "":
                    # Tell the user that a name was not entered and cancel
                    # the submission
                    showerror(message="Please enter a player name with at "
                                      "least one visible character.")
                    return
                # If the player name already exists
                if new_playername in [p.name for p in self.players]:
                    # Tell the user that the name is already in use and
                    # cancel the submission
                    showerror(message="That username is already in use!")
                    return
                # If there is no password and the player has enabled
                # password protection
                if new_password.strip() == "" and password_en:
                    # Tell the user that there is no password and cancel
                    # the submission
                    showerror(message="Please enter a password with at "
                                      "least one visible character.")
                    return

                if password_en:  # If the password was enabled
                    # Hash the password with sha256 and store it to a
                    # variable
                    password_hash = sha256(
                        new_password_input.get().encode()
                    ).hexdigest()
                else:  # If the password was disabled
                    password_hash = None  # Set the password hash to None

                # Create a Player object and add it to the list of players
                self.players.append(Player(
                    new_playername,
                    password_en,
                    password_hash
                ))
                # Destroy the new player window
                new_player_window.destroy()
                # Add the new player to the list of players in the window
                player_list.insert(END, new_playername)
                self.save()  # Save the players to the .json file

            # Create a submit button which will run the submit function
            submit_button = Button(master=new_player_window, text="Create",
                                   command=submit)
            submit_button.pack()

            # While the new player window is in focus
            while new_player_window.focus_displayof():
                # Update the window
                new_player_window.update()

        def check_login(password: str) -> (bool, str or Player):
            """Check if the entered credentials are correct for login and
            account deletion."""
            # If there is no selected username
            if not player_list.curselection():
                # Return a failure due to no selection
                return False, "noSelect"
            # Get the player object with the selected username
            logging_in_player = self.players[player_list.curselection()[0]]
            # If the password hashes match, or if the password is disabled
            if sha256(password.encode()).hexdigest() == \
                    logging_in_player.password_hash or not \
                    logging_in_player.password_en:
                # Return a success and the player object
                return True, logging_in_player
            else:
                # Return a failure due to an incorrect password
                return False, "wrongPassword"

        def login():
            """Callback for loggin a player in"""
            nonlocal logged_in
            # Check the entered credentials
            success, result = check_login(password_var.get())
            if success:  # If the credentials are correct
                # Log in the player
                self.player = result
                logged_in = True
            elif result == "noSelect":  # If a username was not selected
                # Tell the user that a username was not selected
                showerror(message="Please select a username!")
            else:  # If the username and password don't match
                # Tell the user that the username and password don't match
                showerror(message="Incorrect username or password!")

        def guest_login():
            """Callback for logging in as a guest"""
            nonlocal logged_in
            # Ask the user if they are sure they want to use guest mode
            use_guest = askyesno(
                message="Using a guest account will not save your scores."
                        "\nDo you want to continue as a guest?"
            )
            if use_guest:  # If the user is sure
                # Activate guest mode
                self.player = "guest"
                logged_in = True

        def delete_player():
            """Callback for deleting the selected account"""
            # Check the entered credentials
            success, result = check_login(password_var.get())
            if success:  # If the credentials are correct
                # Ask the user if they are sure they want to delete the
                # player
                delete = askyesno(message=f"Are you sure you want to "
                                          f"delete '{result.name}'?")
                if delete:  # If the user is sure
                    # Remove the player from the list of players on-screen
                    player_list.delete(self.players.index(result))
                    password_var.set("")  # Reset the password entry field
                    # Remove the player from the internal list of players
                    self.players.remove(result)
                    self.save()  # Save the players list
            elif result == "noSelect":  # If a username was not selected
                # Tell the user to select a username
                showerror(message="Please select a username!")
            else:  # If the username and password don't match
                # Tell the user that the username and password don't match
                showerror(message="Incorrect username or password!")

        # Create a label to say "Password:"
        password_label = Label(
            master=login_window,
            text="Password:"
        )
        password_label.pack()

        # Create a StringVar and an entry widget to get the password
        password_var = StringVar(master=login_window)
        password_input = Entry(
            master=login_window,
            textvariable=password_var,
            show="✱"
        )
        password_input.pack()

        # Create the buttons

        # Create a frame for the login and guest buttons
        frm_buttons = Frame(master=login_window)
        frm_buttons.pack()
        # Create the login button
        btn_login = Button(
            master=frm_buttons,
            text="Login",
            command=login
        )
        btn_login.pack(side=LEFT)
        # Create the guest button
        btn_guest = Button(
            master=frm_buttons,
            text="Guest",
            command=guest_login
        )
        btn_guest.pack(side=RIGHT)
        # Create the new player button
        btn_new = Button(
            master=login_window,
            text="New Player...",
            command=add_player
        )
        btn_new.pack()
        # Create the delete player button
        btn_del = Button(
            master=login_window,
            text="Delete Player...",
            command=delete_player
        )
        btn_del.pack()

        # While the user is not logged in
        while not logged_in:
            # Update the window
            login_window.update()
        # Destroy the window
        login_window.destroy()

    def serialise_players(self):
        """Serialise the players into json-encodable format."""
        # Return a list of serialised players
        return [this_player.serialise() for this_player in self.players]

    def load(self):
        """Load the players and their highscores from a file"""

        def decorrupt_scores():
            """To be called when the scores file is corrupt"""
            # Tell the user that the file is corrupted
            showwarning(message="Unable to retrieve high scores!\n"
                                "Resetting file...")
            self.save()  # Reset the scores file

        try:
            # Open the scores file
            with open(self.file_name, "r") as scores_file:
                # Read the contents of the scores file
                players_data = load(scores_file)
            # If the type of json data is not a list
            if type(players_data) != list:
                raise TypeError  # Raise a TypeError
        except FileNotFoundError:  # If the file couldn't be found
            # Tell the user that the file couldn't be found
            showwarning(message="Unable to find high scores!\n"
                                "Creating file...")
            self.save()  # Create the scores file
        except EOFError:  # If the file is empty
            decorrupt_scores()  # Decorrupt the scores file
        except JSONDecodeError:  # If the file is not valid json
            decorrupt_scores()  # Decorrupt the scores file
        except TypeError:  # If the type of object is not a list
            decorrupt_scores()  # Decorrupt the scores file
        else:  # If the scores were read successfully
            for player_data in players_data:  # Loop through the list
                # Try to get a player object from the list item
                player_obj = playerfromdict(player_data)
                # If a player object was successfully created
                if player_obj is not None:
                    # Add the player to the list of players.
                    self.players.append(player_obj)

    def save(self):
        """Save the scores to a file"""
        try:
            # Open the scores file
            with open(self.file_name, "w") as scores_file:
                # Save the scores to the file
                dump(self.serialise_players(), scores_file)
        except FileNotFoundError:  # If the file wasn't found
            # Alert the user
            showerror(message="Unable to save!")

    def increase(self, amount: int):
        """Increase the score by an amount"""
        self.score += amount  # Add amount to the score

    def decrease(self, amount: int):
        """Decrease the score by an amount"""
        self.score -= amount  # Take amount from the score

    def draw_score(self):
        """Draw the score at the top of the screen."""
        # Take points off the score for the number of seconds passed

        # If the seconds passed is greater than or equal to 1
        if int(time.time() - self.last_score_decrease) >= 1:
            # Decrease the score by the number of seconds
            self.decrease(int(time.time() - self.last_score_decrease))
            # Set the last time the score was decreased to right now
            self.last_score_decrease = time.time()

        # Clear the previous score
        self.turtle.clear()
        # Draw the new score
        self.turtle.write(
            str(self.score),
            align="center",
            font=("Helvetica", int(y(50)), "normal")
        )


# Create a scorer object with the scores file
scorer = Scorer("assets/scores/scores.json")


class Ship:
    """A class to manage the ship"""

    def __init__(self, y_pos, speed=8):
        self.speed = speed
        self.movement = 0  # 1 or -1, to represent forwards or backwards
        self.turtle = t.Turtle()  # Create a turtle
        # Make the turtle look right
        self.turtle.hideturtle()
        self.turtle.penup()
        self.turtle.goto(0, y_pos)
        self.activate_controls()  # Activate the controls
        self.firing = False  # Not firing right now
        # Save the time since the last bullet
        self.time_last_bullet = time.time() - 60

        self.alive = True  # The player is alive to start

    def draw(self):
        """Draw myself to the screen"""
        self.turtle.clear()  # Clear the previous drawing
        # Get the initial x and y coordinates
        initial_x, initial_y = self.turtle.xcor(), self.turtle.ycor()

        # Draw the main compartment
        self.turtle.fillcolor(230, 230, 230)
        self.turtle.goto(initial_x - x(25), initial_y - y(55))
        self.turtle.begin_fill()
        for point in [(-25, 45), (25, 45), (25, -55)]:
            self.turtle.goto(
                initial_x + x(point[0]),
                initial_y + y(point[1])
            )
        self.turtle.end_fill()

        # Draw the nose cone
        self.turtle.fillcolor(255, 82, 13)
        self.turtle.goto(initial_x - x(25), initial_y + y(45))
        self.turtle.begin_fill()
        for point in [(0, 100), (25, 45)]:
            self.turtle.goto(
                initial_x + x(point[0]),
                initial_y + y(point[1])
            )
        self.turtle.end_fill()

        # Draw the window
        self.turtle.pencolor(255, 82, 13)
        self.turtle.fillcolor(213, 245, 243)
        self.turtle.pensize(5)
        self.turtle.goto(initial_x, initial_y + y(35))
        self.turtle.setheading(0)
        self.turtle.pendown()
        self.turtle.begin_fill()
        self.turtle.circle(x(-15))
        self.turtle.penup()
        self.turtle.end_fill()

        # Draw the side fins
        self.turtle.fillcolor(230, 230, 230)
        for side in [-1, 1]:
            self.turtle.goto(initial_x, initial_y - y(55))
            self.turtle.begin_fill()
            self.turtle.goto(initial_x + x(45 * side), initial_y - y(55))
            self.turtle.setheading(90)
            self.turtle.circle(x(45 * side), 56.33)
            self.turtle.end_fill()

        # Draw the bottom section and the middle fin
        self.turtle.fillcolor(255, 82, 13)
        for side in [-1, 1]:
            self.turtle.goto(initial_x + x(25 * side),
                             initial_y - y(55))
            self.turtle.begin_fill()
            for point in [(1, -55), (1, -20), (25, -20)]:
                self.turtle.goto(
                    initial_x + x(point[0] * side),
                    initial_y + y(point[1])
                )
            self.turtle.end_fill()

        # Draw the exhaust part 1
        self.turtle.fillcolor(0, 53, 227)
        self.turtle.goto(initial_x + x(21), initial_y - y(55))
        self.turtle.begin_fill()
        for point in [(-21, -55), (-21, -58), (21, -58)]:
            self.turtle.goto(
                initial_x + x(point[0]),
                initial_y + y(point[1])
            )
        self.turtle.end_fill()
        # Draw the exhaust part 2
        self.turtle.fillcolor(0, 179, 255)
        self.turtle.goto(initial_x + x(17), initial_y - y(58))
        self.turtle.begin_fill()
        for point in [(-17, -58), (-17, -62), (17, -62)]:
            self.turtle.goto(
                initial_x + x(point[0]),
                initial_y + y(point[1])
            )
        self.turtle.end_fill()

        # Draw the flames
        for flame_no in range(3):
            self.turtle.fillcolor(
                237 + (6 * flame_no),
                160 + (31 * flame_no),
                26 + (76 * flame_no)
            )
            self.turtle.goto(
                initial_x + x(17 - (4 * flame_no)),
                initial_y - y(62)
            )
            self.turtle.begin_fill()
            self.turtle.goto(
                initial_x,
                initial_y - y(90 - (10 * flame_no))
            )
            self.turtle.goto(
                initial_x - x(17 - (4 * flame_no)),
                initial_y - y(62)
            )
            self.turtle.end_fill()

        # Go back to the starting position
        self.turtle.goto(initial_x, initial_y)

    def move(self):
        """Move"""
        self.generate_bullet()  # Generate a bullet if needed

        # If the ship, after moving, will be more left than it should be
        if self.turtle.xcor() + (self.movement * self.speed) < x(-650):
            # Move the ship to the furthest left it can go
            self.turtle.goto(x(-650), self.turtle.ycor())
        # If the ship, after moving, will be more right than it should be
        elif self.turtle.xcor() + (self.movement * self.speed) > x(650):
            # Move the ship to the furthest right it can go
            self.turtle.goto(x(650), self.turtle.ycor())
        else:  # If the ship, after moving, will be within its boundaries
            # Goto the position it will be after moving
            self.turtle.goto(
                self.turtle.xcor() + (self.movement * self.speed),
                self.turtle.ycor()
            )

    def beg_left(self):
        """Start moving left"""
        if self.movement == 0:  # If the ship is not moving
            self.movement = -1  # Start moving left
        else:  # If the ship is moving right
            self.movement = 0  # Stop moving

    def beg_right(self):
        """Start moving right"""
        if self.movement == 0:  # If the ship is not moving
            self.movement = 1  # Start moving right
        else:  # If the ship is moving left
            self.movement = 0  # Stop moving

    def end_left(self):
        """Stop moving left"""
        if self.movement == 0:  # If the ship is not moving
            self.movement = 1  # Start moving right
        else:  # If the ship is moving left
            self.movement = 0  # Stop moving

    def end_right(self):
        """Stop moving right"""
        if self.movement == 0:  # If the ship is not moving
            self.movement = -1  # Start moving left
        else:  # If the ship is moving right
            self.movement = 0  # Stop moving

    def beg_fire(self):
        """Start firing"""
        self.firing = True  # Start firing

    def end_fire(self):
        """Stop firing"""
        self.firing = False  # Stop firing

    def activate_controls(self):
        """Activate the controls."""
        # Bind the arrow keys and space to their respective functions
        screen.onkeypress(self.beg_left, "Left")
        screen.onkeypress(self.beg_right, "Right")
        screen.onkeyrelease(self.end_left, "Left")
        screen.onkeyrelease(self.end_right, "Right")
        screen.onkeypress(self.beg_fire, "space")
        screen.onkeyrelease(self.end_fire, "space")
        # Update the screen's callbacks
        screen.listen()

    def deactivate_controls(self):
        """Deactivate the controls."""
        # Unbind the arrow keys and space from their respective functions
        screen.onkeypress(lambda: None, "Left")
        screen.onkeypress(lambda: None, "Right")
        screen.onkeyrelease(lambda: None, "Left")
        screen.onkeyrelease(lambda: None, "Right")
        screen.onkeypress(lambda: None, "space")
        screen.onkeyrelease(lambda: None, "space")
        # Update the screen's callbacks
        screen.listen()

    def generate_bullet(self):
        """Fire a bullet if necessary"""
        global scorer
        # If the space bar is pressed, and it has been at least half a
        # second since the last bullet was fired
        if self.firing and self.time_last_bullet < time.time() - 0.5:
            # Fire a bullet from the ship's nose
            bullets.append(Bullet(
                self.turtle.xcor(),
                self.turtle.ycor() + 80,
            ))
            # Set the last time a bullet was fired to now
            self.time_last_bullet = time.time()
            # Decrease the score by 1 for firing a bullet
            scorer.decrease(1)

    def intersectspoint(self, x_pos, y_pos) -> bool:
        """Check if the player intersects a point"""
        # Get the x and y coordinates of the ship
        tx = self.turtle.xcor()
        ty = self.turtle.ycor()

        # Quick rectangular hit-box, before more precise hit-box
        if not (tx - x(40) <= x_pos <= tx + x(40) and
                ty - y(55) <= y_pos <= ty + y(100)):
            return False  # Return a no-hit

        # If x_pos and y_pos intersect the fins of the ship
        if tx - x(40) <= x_pos <= tx + x(40) and \
                ty - y(55) <= y_pos <= ty - y(30):
            # Return a hit
            return True
        # If x_pos and y_pos intersect the passenger section of the ship
        if tx - x(25) <= x_pos <= tx + x(25) and \
                ty - y(55) <= y_pos <= ty + y(45):
            # Return a hit
            return True
        # If x_pos and y_pos intersect the nose of the ship
        if (y_pos - ty) < -2.2 * (x_pos - tx) + x(100) and \
                (y_pos - ty) < 2.2 * (x_pos - tx) + x(100) and \
                y_pos - ty > y(45):
            # Return a hit
            return True

        return False  # Return a no-hit

    def dead(self):
        """The player is dead"""
        self.alive = False  # The player is dead
        self.turtle.clear()  # Remove the player drawing from the screen


class Alien:
    """A class to manage an Alien ship"""

    def __init__(self, x_pos, y_pos, level):
        self.turtle = t.Turtle()  # Create a turtle for the alien
        # Make the turtle look right
        self.turtle.penup()
        self.turtle.hideturtle()
        self.turtle.goto(x_pos, y_pos)
        # Set the last time a bullet was fired to a minute ago
        self.time_last_bullet = time.time() - 60
        self.level = level  # Set the level of the alien

        self.alive = True  # The alien is alive to start

    def get_colour(self):
        """Get the colour of the alien based on the level"""
        if self.level == 5:
            return 9, 158, 29
        elif self.level == 10:
            return 50, 100, 168
        else:
            return 168, 50, 50

    def draw(self):
        """Draw myself to the screen"""
        self.turtle.clear()  # Clear the previous drawing
        # Get the initial x and y coordinates
        initial_x, initial_y = self.turtle.xcor(), self.turtle.ycor()

        # Set the fill colour and start filling
        self.turtle.fillcolor(159, 170, 181)
        self.turtle.goto(initial_x - x(40), initial_y - y(8))
        self.turtle.begin_fill()
        # The following was created with help from:
        # https://www.geeksforgeeks.org/draw-ellipse-using-turtle-in-python
        # Draw the body of the alien
        self.turtle.seth(135)
        for _ in range(2):
            self.turtle.circle(x(-60), -90, 5)
            self.turtle.circle(x(-(60 // 20)), -90, 5)
        self.turtle.end_fill()

        # Set the fill colour and start filling
        self.turtle.fillcolor(self.get_colour())
        self.turtle.goto(initial_x - x(24), initial_y)
        self.turtle.begin_fill()
        # Draw the Capsule of the alien
        self.turtle.seth(270)
        self.turtle.circle(x(26.25), -180, 5)
        self.turtle.circle(x(26.25 // 20), -180, 5)
        self.turtle.end_fill()

        # Go back to the starting position
        self.turtle.goto(initial_x, initial_y)

    def intersectspoint(self, x_pos, y_pos) -> bool:
        """Check if the alien intersects a point"""
        # If the point is in the rectangular hit-box
        if self.turtle.xcor() - x(50) <= x_pos <= self.turtle.xcor() + \
                x(50) and \
                self.turtle.ycor() - y(27) <= y_pos <= self.turtle.ycor():
            return True  # Return a hit
        else:
            return False  # Return a no-hit

    def generate_bullet(self, alien_count):
        """Fire a bullet"""
        # If a random number scaled to the number of aliens and the alien's
        # level is 0
        if randint(
                0,
                int(1500 - 24 * (55 - ((2*self.level*alien_count) / 12)))
        ) == 0:
            # If the last bullet was fired more than 2 seconds ago
            if self.time_last_bullet < time.time() - 2:
                # Fire a bullet at the player
                bullets.append(Bullet(
                    self.turtle.xcor(),
                    self.turtle.ycor(),
                    y(-4),
                    fired_by_player=False,
                    color=self.get_colour()
                ))
                # Set the time that the last bullet was fired at to now
                self.time_last_bullet = time.time()

    def dead(self):
        """The alien is dead"""
        if self.level == 5:
            self.alive = False  # The alien is dead
            self.turtle.clear()  # Remove the alien drawing from the screen
        else:
            self.level -= 5  # Decrease the level by 5


player = Ship(y(-350))  # Create the player ship

# Create the aliens
aliens = []
for alien_x in range(-550, 551, 110):
    for alien_y in range(0, 301, 75):
        if alien_y <= 75:
            alien_level = 5
        elif alien_y <= 255:
            alien_level = 10
        else:
            alien_level = 15
        aliens.append(Alien(x(alien_x), y(alien_y), alien_level))


def end_screen(win: bool):
    """Show the end screen"""
    # Increase or decrease the score for winning or losing
    if win:
        scorer.increase(50)
    else:
        scorer.decrease(50)

    # Clear the screen
    screen.clearscreen()
    screen.bgcolor(0, 0, 0)

    scorer.draw_score()  # Draw the score

    # Create a turtle to draw the end screen stuff
    end_turtle = t.Turtle()
    # Make the turtle look right and go to the right position
    end_turtle.hideturtle()
    end_turtle.penup()
    end_turtle.goto(pos(0, 0))
    end_turtle.color(1, 1, 1)

    if win:  # If the game ended because the player won
        # Write on the screen that the player won
        end_turtle.write(
            "Triumph!",
            align="center",
            font=("Helvetica", int(y(50)), "normal")
        )
    else:  # If the game ended because the player lost
        # Write on the screen that the player lost
        end_turtle.write(
            "Defeat!",
            align="center",
            font=("Helvetica", int(y(50)), "normal")
        )
    wait_ms(500, screen)  # Wait half a second, while updating the screen
    # Go to the position for writing the comment
    end_turtle.goto(pos(0, -25))

    if win:  # If the player won
        # Write a random positive comment on the screen
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
    else:  # If the player lost
        # Write a random negative comment on the screen
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

    # Deal with the high score
    high = scorer.game_over()  # Save the highscore (if any)
    if high > 0:  # If there was some form of high score
        wait_ms(500, screen)
        end_turtle.goto(pos(0, 320))
    if high == 1:  # If there is a personal best
        end_turtle.write(
            "New Personal Best!!",
            align="center",
            font=("Helvetica", int(y(20)), "normal")
        )
    elif high == 2:  # If there is a high score
        end_turtle.write(
            "New High Score!!",
            align="center",
            font=("Helvetica", int(y(20)), "normal")
        )

    wait_ms(500, screen)  # Wait a second, while updating the screen
    # Go to the position for writing the exit text
    end_turtle.goto(pos(0, -50))
    # Write the exit text
    end_turtle.write(
        "Press Space to exit.",
        align="center",
        font=("Helvetica", int(y(15)), "normal")
    )

    done = False  # The player has not pressed space

    def finish():
        """Callback for when the player presses space"""
        nonlocal done
        done = True  # The player has pressed space

    # Tell the window to call finish when space is pressed
    screen.onkeypress(finish, "space")
    screen.listen()

    # Continue updating the window while the player has not pressed space
    while not done:
        screen.update()

    scorer.save()  # Save the scores

    return


# Set the last frame time to 10ms ago
last_frame_time = time.time_ns() / 1_000_000 - 10

alien_direction = 1  # Set the direction of the aliens to right


def alien_speed():
    """Get the alien speed"""
    # Get a speed for the aliens that factors in the number of aliens that
    # have been shot already
    return x(0.175 + (0.175 * (55 - len(aliens))))


while True:  # Forever
    # Get the current time in ms
    current_time = time.time_ns() / 1_000_000
    # Get the time since the last frame
    time_diff = current_time - last_frame_time
    # Repeat for the number of frames the computer missed due to lag
    # NB: the code aims for 33.3 fps
    for _ in range(int(time_diff / 10)):
        # If all the aliens are dead
        if not aliens:
            # End the game with the player winning
            end_screen(True)
            exit()

        # Move the player
        player.move()
        # Draw the player
        player.draw()

        # Get the alien x-coordinates, minimum x-coordinates, maximum
        # x-coordinates, y-coordinates and minimum y-coordinates
        alien_xs = [alien.turtle.xcor() for alien in aliens]
        max_alien_x = max(alien_xs)
        min_alien_x = min(alien_xs)
        alien_ys = [alien.turtle.ycor() for alien in aliens]
        min_alien_y = min(alien_ys)

        # If the aliens are too close to the player, or if the player is
        # dead
        if min_alien_y < y(-180) or (not player.alive):
            # End the game with the player losing
            end_screen(False)
            exit()


        def move_aliens_down():
            """Move the aliens down a row"""
            for alien in aliens:  # Loop through the aliens
                # Move the alien down
                alien.turtle.goto(
                    alien.turtle.xcor(),
                    alien.turtle.ycor() - y(10)
                )


        # If the aliens are further right than they should be
        if max_alien_x >= x(650):
            alien_direction = -1  # Set the alien direction to left
            move_aliens_down()  # Move the aliens down
        elif min_alien_x <= x(-650):
            alien_direction = 1  # Set the alien direction to right
            move_aliens_down()  # Move the aliens down

        aliens_to_delete = []  # Make a list of aliens to be deleted
        # Loop through the aliens which aren't deleted
        for alien in aliens:
            if alien.alive:  # If the alien is still alive
                # Move the alien in the right direction and by the right
                # speed
                alien.turtle.goto(
                    alien.turtle.xcor()
                    + (alien_speed() * alien_direction),
                    alien.turtle.ycor()
                )
                # Check if the alien is at the bottom of its column
                alien_bottom_of_column = True
                for alien_2 in aliens:
                    if alien_2.turtle.xcor() == alien.turtle.xcor() and \
                            alien_2.turtle.ycor() < alien.turtle.ycor():
                        alien_bottom_of_column = False
                        break
                # If the alien is at the bottom of its column
                if alien_bottom_of_column:
                    alien.generate_bullet(len(aliens))  # Generate a bullet

                alien.draw()  # Draw the alien to the screen
            else:  # If the alien is dead
                # Add the alien to the list of aliens to delete
                aliens_to_delete.append(alien)
                # Increase the score relative to the alien's level
                scorer.increase(alien.level)

        # Loop through the aliens to be deleted
        for alien in aliens_to_delete:
            aliens.remove(alien)  # Remove the alien from the list
            del alien  # Delete the alian from memory

        bullets_to_delete = []  # Make a list of bullets to be deleted
        for bullet in bullets:  # Loop through the bullets
            bullet.move(player, aliens)  # Move the bullet
            # If the bullet is off-screen
            if bullet.turtle.ycor() < y(-500):
                # Add the bullet to the list of bullets to delete
                bullets_to_delete.append(bullet)

        # Loop through the bullets to be deleted
        for bullet in bullets_to_delete:
            bullet.turtle.hideturtle()  # Hide the bullet
            bullets.remove(bullet)  # Remove the alien from the list
            del bullet  # Delete the bullet from memory

    # Set the last frame time to now
    last_frame_time = time.time_ns() / 1_000_000
    scorer.draw_score()  # Draw the score to the screen
    screen.update()  # Update the screen
