from ttk import Style
from Tkinter import *
from PIL import Image, ImageTk
from Tkinter import E, S, N, W
from os import *

from GameService import GameService

WINDOW_HEIGHT = 450
WINDOW_WIDTH = 550
BOARD_WIDTH = WINDOW_WIDTH * 55 / 100
BOARD_HEIGHT = WINDOW_HEIGHT * 60 / 100
WINDOW_MARGIN_X = WINDOW_WIDTH * 20 / 100
WINDOW_MARGIN_Y = 10
POPUP_WIDTH = 600
POPUP_HEIGHT = 350

"""
This class is responsible for displaying the interface of the game 
and handle user actions.
"""


class TileGame:

    def __init__(self, no_tiles):
        self.no_tiles = no_tiles
        self.game_service = GameService()
        self.__init_window()
        self.__init_tiles()
        self.__init_board_panel()
        self.__init_button_panel()

    def __init_window(self):
        self.window = Tk()
        self.window.title('All lights out')
        self.window.geometry(
            WINDOW_WIDTH.__str__() + 'x' + WINDOW_HEIGHT.__str__())
        self.window.minsize(250, 350)
        self.window.tk.call("source", "ttk-theme/forest-dark.tcl")
        style = Style()
        style.theme_use("forest-dark")

    def __init_board_panel(self):
        self.board_panel = PanedWindow(master=self.window,
                                       width=BOARD_WIDTH,
                                       height=BOARD_HEIGHT)
        self.board_panel.pack(fill=BOTH, expand=1, side=TOP,
                              padx=WINDOW_MARGIN_X,
                              pady=WINDOW_MARGIN_Y)
        lights_on = self.game_service.get_lights_state()
        for i in range(self.no_tiles):
            # set column and row dimensions to handle window resizing
            self.board_panel.rowconfigure(i, weight=1)
            self.board_panel.columnconfigure(i, weight=1)
            self.tiles.append([])

            for j in range(self.no_tiles):
                self.tiles[i].append(Button(master=self.board_panel,
                                            image=self.tile_state[
                                                lights_on[i][j]],
                                            command=lambda x=i,
                                                           y=j:
                                            self.__on_flip(
                                                x, y)))
                self.tiles[i][j].grid(row=i, column=j,
                                      sticky=N + S + E + W)

    def __init_tiles(self):
        self.tiles = []
        image_led_on = ImageTk.PhotoImage(
            Image.open("images/yellowButton.png").resize((
                BOARD_WIDTH / self.no_tiles,
                BOARD_HEIGHT / self.no_tiles)))
        image_led_off = ImageTk.PhotoImage(
            Image.open("images/greyButton.png").resize((
                BOARD_WIDTH / self.no_tiles,
                BOARD_HEIGHT / self.no_tiles)))
        self.tile_state = {0: image_led_off, 1: image_led_on}

        self.image_congratulations = ImageTk.PhotoImage(
            Image.open("images/congratulations.png").resize((
                POPUP_WIDTH,
                POPUP_HEIGHT / 2)))

        self.no_frames = self.__count_images_in_gif_dir(
            "images/animatedButton")
        self.frames = [ImageTk.PhotoImage(Image.open(
            "images/animatedButton/greenButton{}.png".format(
                i + 1)).resize((BOARD_WIDTH / self.no_tiles,
                                BOARD_HEIGHT / self.no_tiles))) for i
                       in range(self.no_frames)]
        self.hint_animation_id = None
        self.solution_animation_id = None

    @staticmethod
    def __count_images_in_gif_dir(dir_name):
        no_images = 0
        for base, dirs, files in walk(dir_name):
            for _ in files:
                no_images += 1
        return no_images

    def __refresh_board(self):
        lights_on = self.game_service.get_lights_state()
        for i in range(self.no_tiles):
            for j in range(self.no_tiles):
                self.tiles[i][j].config(
                    image=self.tile_state[lights_on[i][j]])

    def __init_button_panel(self):
        self.button_panel = PanedWindow(master=self.window)
        self.button_panel.pack(fill=BOTH, expand=0, side=TOP,
                               padx=WINDOW_MARGIN_X,
                               pady=WINDOW_MARGIN_Y)
        self.button_panel.rowconfigure(0, weight=1)
        self.button_panel.columnconfigure(0, weight=1)
        self.button_panel.columnconfigure(1, weight=1)
        self.button_panel.columnconfigure(2, weight=1)
        self.hint_button = Button(master=self.button_panel,
                                  text="Hint",
                                  command=self.__on_hint)
        self.hint_button.grid(row=0, column=0)
        self.reset_button = Button(master=self.button_panel,
                                   text="Reset",
                                   command=self.__on_reset)
        self.reset_button.grid(row=0, column=1)
        self.solve_button = Button(master=self.button_panel,
                                   text="Solve",
                                   command=self.__on_solve)
        self.solve_button.grid(row=0, column=2)
        self.new_game_button = Button(master=self.button_panel,
                                      text="New game",
                                      command=self.__on_new_game)
        self.new_game_button.grid(row=0, column=3)

    def __display_results_popup(self, game_solved_by_player):
        popup_dialog = Toplevel(self.window)
        popup_dialog.geometry(
            str(POPUP_WIDTH) + "x" + str(POPUP_HEIGHT))
        popup_dialog.title("Game results")
        popup_dialog.resizable(False, False)
        popup_dialog.columnconfigure(0, weight=1)
        popup_dialog.rowconfigure(0, weight=3)
        popup_dialog.rowconfigure(1, weight=1)
        popup_dialog.rowconfigure(2, weight=2)

        # display the congratulatory message only if the puzzle was
        # solved by the player (and not by clicking on the Solve button)
        if game_solved_by_player:
            Label(popup_dialog,
                  image=self.image_congratulations).grid(
                row=0, column=0)
            Label(popup_dialog, text="You solved the game in " + str(
                self.game_service.get_no_steps_in_game_session()) + " steps.",
                  font=('Mistral 17 bold')).grid(row=1, column=0)

        Label(popup_dialog,
              text="The shortest solution consisted of " + str(
                  self.game_service.length_of_shortest_solution_from_initial_state()) + " steps.",
              font=('Mistral 15 bold')).grid(
            row=2 if game_solved_by_player else 0, column=0)

    def __stop_running_hint_animations(self, enable_hint_button=True):
        if self.hint_animation_id is not None:
            self.window.after_cancel(self.hint_animation_id)
            self.hint_animation_id = None
            # enable_hint_button determines if it is needed to re-enable
            # the button for hint after the animation is stopped
            self.hint_button.config(
                state=NORMAL if enable_hint_button else DISABLED)

    def __stop_running_solution_animations(self):
        if self.solution_animation_id is not None:
            self.window.after_cancel(self.solution_animation_id)
            self.solution_animation_id = None
            self.solve_button.config(state=NORMAL)
            # re-enable the button Hint after the animation is stopped
            self.hint_button.config(state=NORMAL)

    def __flip_tile(self, x, y, re_enable_hint_button=True,
                    game_solved_by_player=True):
        # stop any running hint animations
        self.__stop_running_hint_animations(
            enable_hint_button=re_enable_hint_button)
        self.game_service.switch_light(x, y)
        self.__refresh_board()
        if self.game_service.won_game_session():
            # delay showing the results to display the board after
            # the last step
            self.window.after(500,
                              lambda: self.__display_results_popup(
                                  game_solved_by_player=game_solved_by_player))

    def __on_flip(self, x, y):
        # tiles cannot be flipped while the solution simulation is
        # running
        if self.solution_animation_id is not None:
            return
        self.__flip_tile(x, y)

    def __animate_hint(self, x, y, index=0):
        self.tiles[x][y].config(image=self.frames[index])
        index = (index + 1) % self.no_frames
        self.hint_animation_id = \
            self.window.after(100, lambda: self.__animate_hint(
                x, y, index))

    def __on_hint(self):
        # show hint only if the game has not yet been won
        if not self.game_service.won_game_session():
            # disable the button until the hint animation is stopped:
            # only 1 hint should be played at a time
            self.hint_button.config(state=DISABLED)
            (x, y) = self.game_service.get_hint()
            self.__animate_hint(x, y)

    def __on_reset(self):
        # stop all running animations
        self.__stop_running_hint_animations()
        self.__stop_running_solution_animations()
        self.game_service.reset_game_session()
        self.__refresh_board()

    def __next_hint(self, x, y):
        self.__flip_tile(x, y, re_enable_hint_button=False,
                         game_solved_by_player=False)
        self.__animate_solution()

    def __animate_solution(self):
        # run simulation only if the game has not yet been won
        if self.game_service.won_game_session():
            self.__stop_running_solution_animations()
            return
        (x, y) = self.game_service.get_hint()
        self.__animate_hint(x, y)
        self.solution_animation_id = \
            self.window.after(1500, lambda: self.__next_hint(x, y))

    def __on_solve(self):
        # stop previous hint animations and disable hint button
        self.__stop_running_hint_animations(enable_hint_button=False)
        self.hint_button.config(state=DISABLED)
        self.__refresh_board()
        # disable the solve button until the animation is running
        self.solve_button.config(state=DISABLED)
        self.__animate_solution()

    def __on_new_game(self):
        # stop all running animations
        self.__stop_running_hint_animations()
        self.__stop_running_solution_animations()
        self.game_service.init_new_game_session()
        self.__refresh_board()

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    game = TileGame(no_tiles=5)
    game.run()
