import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np


class GUI:

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.frames = {}
        self.buttons = {}

    def set_params(self) -> None:
        self.root.geometry("1000x800")
        self.root.title("Snickle")
        self.root.protocol("WM_DELETE_WINDOW", self._quit)      # set exit window protocol to _quit (kill mainloop and end program)

    def create_widgets(self) -> None:
        fig = self._plot_waveform()
        self.display = FigureCanvasTkAgg(fig, master=self.root)      # widget to display a graphic of a waveform
        self.display.draw

    def pack_widgets(self) -> None:
        self.display.get_tk_widget().pack(      # create and pack a widget for the figure canvas
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True
        )

    def _quit(self) -> None:        # ensures the mainloop is killed and the program ends
        self.root.quit()            # kills mainloop
        self.root.destroy()         # necessary on windows or wsl when using matplotlib

    def _plot_waveform(self):
        """ Return a plot of a waveform passed as input. """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.tick_params(
            axis = 'both',           # changes apply to both axes
            which = 'both',          # both minor and major ticks affected
            bottom = False,          # turn off ticks along the bottom edge
            top = False,             
            left = False,
            right = False,
            labelbottom = False,     # turn off tick labels on the bottom edge
            labelleft = False
        )

        t = np.arange(0, 3, .01)
        s = np.sin(2 * np.pi * t)

        wave = ax.plot(t, s)
        
        return fig


def main():
    gui = GUI()
    gui.set_params()
    gui.create_widgets()
    gui.pack_widgets()
    gui.root.mainloop()

if __name__ == "__main__":
    main()