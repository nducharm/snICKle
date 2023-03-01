import numpy as np

from scipy.fft import fft, fftfreq, fftshift
from scipy import signal

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import tkinter as tk

import sounddevice as sd


# sampling rate is globally fixed at the CD standard of 44_100 Hz
sampling_rate = 44_100

# sounddevice defaults for recording and playback
sd.default.samplerate = sampling_rate
sd.default.channels = 1


class GUI:

    def __init__(self) -> None:
        self.root = tk.Tk()

        self._set_window_params()
        
        # Set default signal duration and sampling times.
        self.duration = 5
        self.times = np.linspace(
            0, self.duration, self.duration * sampling_rate
            )
        # Intialize signal attribute as the 0 function.
        self.signal = np.sin(self.times)
        

        # Plot waveform of recorded signal.
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self._set_pyplot_params()
        # Create figure canvas for displaying matplotlib output.
        self.display = FigureCanvasTkAgg(self.fig, master=self.root)
        # Create and pack a widget for the figure canvas.
        self.display.get_tk_widget().pack(
            side='top',
            fill='both',
            expand=True
        )
        self.waveform = self.ax.plot(self.times, self.signal)
        self._plot_waveform()


        # dft_button = tk.Button(
        # self.root, text='Frequency Domain', command=self._fourier_transform
        # )
        # dft_button.pack()

        # idft_button = tk.Button(
        # self.root, text='Time Domain', command=self._plot_waveform
        # )
        # idft_button.pack()

        modify_button = tk.Button(
            self.root, text='APPLY FILTER', command=self._filter
            )
        modify_button.pack()

        record_button = tk.Button(
            self.root, text='RECORD', command=self._record
            )
        record_button.pack()

        play_button = tk.Button(
            self.root, text='PLAY', command=self._play
            )
        play_button.pack()

    def _quit(self) -> None:
        """Quit and destroy Tk window.
        
        The default `root.quit` method is not sufficient to halt the
        program because of some interaction with `matplotlib`, so we
        call both `root.quit` and `root.destroy`.
        """
        self.root.quit()
        self.root.destroy()

    def _set_window_params(self) -> None:
        """Set parameters for the Tk window.
        
        Sets title, window geometry, quit protocol, etc..
        """
        self.root.title('snICKle')

        # Set window X button command.
        self.root.protocol('WM_DELETE_WINDOW', self._quit)
        
        # Set default window size to be maximized to screen dimensions.
        self.root.attributes('-zoomed', True)

    def _set_pyplot_params(self) -> None:
        """Set parameters for the axes displayed on the figure canvas.
        
        Axes tick parameters, line properties, etc.. Just makes the
        constructor code less busy.
        """
        pass

    def _record(self) -> None:
        """Record user input to `self.signal` and update the graph.
        
        Calls the relevant function from sounddevice (using our
        defaults). Execution of the program is paused while the
        recording completes. After new data is written out to 
        `self.signal`, `_plot_waveform` is called to update the graphed
        waveform on the figure canvas.
        """
        signal_in = sd.rec(self.duration * sampling_rate)
        # Pause the program while recording completes.
        sd.wait()
        self.signal = signal_in
        self._plot_waveform()
    
    def _play(self) -> None:
        """Play back `self.signal`. 
        
        Simply calls the relevant function from sounddevice.
        """
        sd.play(self.signal)

    def _plot_waveform(self) -> None:
        """Draw self.signal as a waveform on the Tk figure canvas. 
        
        The Tk figure canvas is associated with the figure `self.fig`,
        which has an axes `self.ax`. We want to redraw the waveform
        displayed on the canvas, rather than stacking new waveforms on 
        top of existing ones; to do this, we reach into `self.waveform`,
        the plot that is shown on `self.ax`, to access its associated
        line object and update the y-axis data to reflect the current
        state of `self.signal`. We also update the x-axis data in case
        the signal duration has changed.
        """
        # Get plot's line object and change its x and y data.
        waveform_line = self.waveform[0]
        waveform_line.set_xdata(self.times)
        waveform_line.set_ydata(self.signal)
        self.display.draw()

    def _fourier_transform(self) -> None:
        """Display DFT of `self.signal` on the figure canvas.
        
        Plots the amplitude portion of the amplitude-phase form of the
        DFT on the figure canvas.
        """
        signalft = fftshift(fft(self.signal))
        freq = fftshift(fftfreq(self.times.shape[-1]))

        # Calling `_plot_waveform` here would cause trouble because we
        # would have to overwrite `self.signal` and `self.times`. Inst-
        # ead we change the x and y data in `self.waveform` again with-
        # out touching any attributes we don't want to overwrite. 
        waveform_line = self.waveform[0]
        waveform_line.set_xdata(freq)
        waveform_line.set_ydata(signalft.real)
        self.display.draw()

    def _filter(self) -> None:
        """Placeholder to test various digital filter designs."""
        pass