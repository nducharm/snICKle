import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import numpy as np

import sounddevice as sd


sampling_rate = 44_100      # sampling rate should be globally constant

sd.default.samplerate = sampling_rate       # set sounddevice defaults for recording and playback
sd.default.channels = 1

class GUI:

    def __init__(self) -> None:     # GUI code all lives inside the init method except starting mainloop
        self.root = tk.Tk()
        t = np.linspace(0, 4, 4 * sampling_rate)
        self.signal = np.cos(2 * np.pi * t * 342)

        self.root.title('SNICKLE')
        
        self.root.protocol('WM_DELETE_WINDOW', self._quit)      # set exit window button cmd to _quit (kill mainloop and end program)

        self._plot_waveform()

        self.plot_button = tk.Button(self.root, text='PLOT', command=self._plot_waveform)
        self.plot_button.pack()

        self.record_button = tk.Button(self.root, text='RECORD', command=self._record)
        self.record_button.pack()

        self.play_button = tk.Button(self.root, text='PLAY', command=self._play)
        self.play_button.pack()

    def _quit(self) -> None:        # ensures the mainloop is killed and the program ends
        self.root.quit()            # kills mainloop
        self.root.destroy()         # necessary on windows or wsl when using matplotlib

    def _record(self) -> None:
        signal_in = sd.rec(4)
        sd.wait()
        self.signal = signal_in
        return None
    
    def _play(self) -> None:
        sd.play(self.signal)
        return None

    def _plot_waveform(self) -> None:
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

        signal_length = len(self.signal)
        signal_duration = signal_length // sampling_rate

        t = np.linspace(0, signal_duration, signal_length)

        ax.plot(t, self.signal)

        display = FigureCanvasTkAgg(fig, master=self.root)      # widget to display a graphic of our waveform
        display.draw
        display.get_tk_widget().pack(      # create and pack a widget for the figure canvas
            side=tk.TOP,
            fill=tk.BOTH,
            expand=True
        )
        
        return None


def main():
    gui = GUI()
    gui.root.mainloop()

if __name__ == '__main__':
    main()