from ttk import Style

from tkinter import *
from PIL import Image, ImageTk
from tkinter import E, S, N, W
from os import *
from GameService import GameService

WINDOW_HEIGHT = 450
WINDOW_WIDTH = 550
BOARD_WIDTH = WINDOW_WIDTH * 55 / 100
BOARD_HEIGHT = WINDOW_HEIGHT * 60 / 100
WINDOW_MARGIN_X = WINDOW_WIDTH * 20 / 100
WINDOW_MARGIN_Y = 10

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
        self.tile_state = {0: image_led_on, 1: image_led_off}

        self.no_frames = self.__count_images_in_gif_dir(
            "images/animatedButton")
        self.frames = [ImageTk.PhotoImage(Image.open(
            "images/animatedButton/rotatingButton{}.png".format(
                i + 1)).resize((BOARD_WIDTH / self.no_tiles,
                                BOARD_HEIGHT / self.no_tiles))) for i
                       in range(self.no_frames)]
        self.hint_animation_id = None
        self.solution_animation_id = None

    def __count_images_in_gif_dir(self, dir_name):
        noImages = 0
        for base, dirs, files in walk(dir_name):
            for _ in files:
                noImages += 1
        return noImages

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
                                  command=self.__on_hint).grid(row=0,
                                                               column=0)
        self.reset_button = Button(master=self.button_panel,
                                   text="Reset",
                                   command=self.__on_reset).grid(
            row=0, column=1)
        self.solve_button = Button(master=self.button_panel,
                                   text="Solve",
                                   command=self.__on_solve).grid(
            row=0, column=2)

    def __animate_hint(self, x, y, index):
        self.tiles[x][y].config(image=self.frames[index])
        index = (index + 1) % self.no_frames
        self.hint_animation_id = self.window.after(50,
                                                   lambda:
                                                   self.__animate_hint(
                                                       x, y, index))

    def __on_flip(self, x, y):
        if self.hint_animation_id is not None:
            self.window.after_cancel(self.hint_animation_id)
        self.game_service.switch_light(x, y)
        self.__refresh_board()

    def __on_hint(self):
        (x, y) = self.game_service.get_hint()
        self.__animate_hint(x, y, index=0)

    def __on_reset(self):
        self.game_service.reset_game_session()
        self.__refresh_board()

    def __animate_solution(self):
        if self.game_service.won_game_session():
            self.window.after_cancel(self.solution_animation_id)
        next_hint = self.game_service.get_hint()
        self.__on_flip(next_hint[0], next_hint[1])
        self.solution_animation_id = self.window.after(200,
                                                       self.__animate_solution)

    def __on_solve(self):
        self.__animate_solution()

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    game = TileGame(no_tiles=5)
    game.run()
