"""The main menu file"""
import tkinter as tk
from functools import partial


class Game:
    """A class to store the data for a game"""
    def __init__(self, name, description, run_func: callable):
        self.name = name
        self.description = description
        self.run = run_func


class Menu:
    """The main menu, and launcher of games"""

    # Note: This class is largely based on and partly copied from the
    # get-sentral python package, which is publicly available on PyPi, GitHub
    # and other places:
    # https://pypi.org/project/SentralTimetable/
    # https://j-j-b-j.github.io/get-sentral/
    # https://github.com/J-J-B-J/get-sentral
    # Get-Sentral is made and maintained by Safin Zaman and myself.
    # https://github.com/J-J-B-J/get-sentral/graphs/contributors
    # The code was copied from the 'App' class in the file 'app.py' in the base
    # directory:
    # https://github.com/J-J-B-J/get-sentral/blob/f7d9a2f1664df7e050e7c4487d2b4a5691693a57/app.py#L22
    # This code in particular was written by me, as shown in the blame view:
    # https://github.com/J-J-B-J/get-sentral/blame/main/app.py
    # The two lines that Safin wrote, 763 and 767, were not used in this class.
    # I have not submitted this code in any other assessment task.

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Games")
        self.window.geometry("500x500")
        self.window.resizable(False, False)

        self.game_range_start = 0
        self.games = []

        self.section_objects = []

    def destroy_section_objects(self):
        """Destroy all the objects in the section_objects list."""
        for object_ in self.section_objects:
            object_.destroy()
        self.section_objects = []

    def create_increase_decrease(self, frame: tk.Frame, counter,
                                 increment: int, data: list, increase_range,
                                 decrease_range):
        """
        Create the increase and decrease buttons for a page.
        :param frame: The frame in which to pack the buttons
        :param counter: The variable which keeps track of the count
        :param increment: The amount to increment the counter by
        :param data: The list of data that is being displayed
        :param increase_range: The callback for when the increase button is
        pressed
        :param decrease_range: The callback for when the decrease button is
        pressed
        """
        btn_increase_range = tk.Button(
            frame,
            text=">",
            width=10
        )
        self.section_objects.append(btn_increase_range)
        btn_increase_range.pack(side=tk.RIGHT)
        if counter + increment < len(data):
            btn_increase_range.bind("<Button-1>", increase_range)
        else:
            btn_increase_range.config(state=tk.DISABLED)

        btn_decrease_range = tk.Button(
            frame,
            text="<",
            width=10
        )
        self.section_objects.append(btn_decrease_range)
        btn_decrease_range.pack(side=tk.LEFT)
        if counter > 0:
            btn_decrease_range.bind("<Button-1>", decrease_range)
        else:
            btn_decrease_range.config(state=tk.DISABLED)

    def menu(self):
        """Run the menu"""
        self.destroy_section_objects()
        frm_games = tk.Frame(self.window, width=500, height=450)
        self.section_objects.append(frm_games)
        frm_games.pack()

        def increase_range(*_):
            """Increase the range of notices shown"""
            self.game_range_start += 5
            self.menu()

        def decrease_range(*_):
            """Decrease the range of notices shown"""
            self.game_range_start -= 5
            self.menu()

        def open_notice(this_game: Game, *_):
            """Show the detail view for a game"""
            game_window = tk.Tk()
            game_window.title(this_game.name)
            game_window.geometry('500x150')
            game_window.focus_set()
            game_window.bind(
                "<Escape>",
                lambda _: game_window.destroy()
            )

            lbl_name = tk.Label(
                game_window,
                text=this_game.name,
                font=("Arial", 20)
            )
            lbl_name.pack(side=tk.TOP)

            lbl_description = tk.Label(
                game_window,
                text=this_game.description,
                wraplength=490
            )
            lbl_description.pack(side=tk.TOP)

            game_window.mainloop()

        for game in self.games[self.game_range_start:self.game_range_start+5]:
            frm_game = tk.Frame(frm_games, width=500, height=50)
            self.section_objects.append(frm_game)
            frm_game.pack()

            lbl_notice_title = tk.Label(
                frm_game,
                text=game.title,
                width=50,
                height=2,
                wraplength=390,
                borderwidth=3,
                relief="raised"
            )
            self.section_objects.append(lbl_notice_title)
            lbl_notice_title.pack(side=tk.LEFT)
            lbl_notice_title.bind(
                "<Button-1>",
                partial(open_notice, game)
            )

        self.create_increase_decrease(
            frm_games,
            self.game_range_start,
            5,
            self.games,
            increase_range,
            decrease_range
        )

    def run(self):
        """Run the app."""
        self.menu()
        self.window.mainloop()


def main():
    """The main function"""
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    main()
