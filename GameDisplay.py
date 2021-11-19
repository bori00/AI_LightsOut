import tkinter as tk
from tkinter import E, S, N, W

WINDOW_HEIGHT = 500
WINDOW_WIDTH = 500
WINDOW_MARGIN_X=50
WINDOW_MARGIN_Y=50
SAMPLE_RATE=2

class TileGame:

    def __init__(self, noTiles):
        self.noTiles = noTiles
        self.initWindow()
        self.tiles = []
        self.displayBoardPanel()

    def initWindow(self):
        self.window = tk.Tk()
        self.window.title('All lights out')
        self.window.geometry(
            WINDOW_WIDTH.__str__() + 'x' + WINDOW_HEIGHT.__str__())
        self.window.minsize(250,
                            350)

    def displayBoardPanel(self):
        self.boardPanel = tk.PanedWindow(master=self.window)
        self.boardPanel.pack(fill=tk.BOTH, expand=1, side=tk.TOP, padx=WINDOW_MARGIN_X,pady=WINDOW_MARGIN_Y)
        self.image = tk.PhotoImage(file="images/yellowButton.png")\
                        .subsample(
                        self.noTiles*SAMPLE_RATE,
                        self.noTiles*SAMPLE_RATE)
        self.ledOff = tk.PhotoImage(file="images/greyButton.png")
        for i in range(self.noTiles):
            # set column and row dimensions to handle window resizing
            self.boardPanel.rowconfigure(i, weight=1)
            self.boardPanel.columnconfigure(i, weight=1)
            self.tiles.append([])

            for j in range(self.noTiles):
                self.tiles[i].append(tk.Button(master=self.boardPanel,
                                               image=self.image))
                self.tiles[i][j].grid(row=i, column=j,
                                      sticky=N + S + E + W)


    def displayButtonPanel(self):
        self.buttonPanel = tk.PanedWindow(master=self.window)
        self.buttonPanel.pack(fill=tk.BOTH, expand=0,side=tk.RIGHT,
                              padx=WINDOW_MARGIN_X,
                              pady=WINDOW_MARGIN_Y)
        self.startButton = tk.Button(master=self.buttonPanel,
                                               text="Start")
        self.startButton.pack(side=tk.BOTTOM)

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    game = TileGame(noTiles=5)
    game.run()
