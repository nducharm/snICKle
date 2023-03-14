import numpy as np

import matplotlib as plt

import tkinter as tk
from tkinter import ttk

import sounddevice as sd

sampling_rate = 44_100

class SignalData():
    def __init__(self, signal) -> None:
        self.duration = tk.IntVar(value=10)
        self.sampletimes = np.linspace(
            0, self.duration.get(), self.duration.get() * sampling_rate
        )
        self.signal = signal

        self.fig_time = plt.figure()
        self.fig_freq = plt.figure()


class GUI():
    def __init__(self, signalobj) -> None:
        self.signalobj = signalobj
        self.root = tk.Tk()

        self.set_window_params()

        Ribbon()


    def _set_window_params(self) -> None:
        """Set parameters for the Tk window.
        
        Sets title, window geometry, quit protocol, etc..
        """
        self.root.title('snICKle')

        # Reset window X button command.
        def newquit():
            self.root.quit()
            self.root.destroy()
        self.root.protocol('WM_DELETE_WINDOW', newquit)
        
        # Set default window size to be maximized to screen dimensions on Linux.
        self.root.attributes('-zoomed', True)


class Canvas():
    def __init__(self, signalobj) -> None:
        self.signalobj = signalobj

        # Canvas notebook code goes here.

    def plot_waveform(self) -> None:
        pass

    def plot_dft(self) -> None:
        pass


class Ribbon():
    def __init__(self, signalobj, canvasobj, parent) -> None:
        self.signalobj = signalobj

        frame = tk.Frame(
            parent, borderwidth=2, relief='raised'
        )

        # Control recording duration.
        duration_slider = tk.Scale(
            frame, label='Recording Length', orient='horizontal',
            from_=5, to=20, variable=self.signalobj.duration, 
            command=self._update_times, length=182
        )
        duration_slider.place(x=5)

        record_button = tk.Button(
            frame, text='RECORD', command=self._record
        )
        record_button.place(relheight=0.9, width=97, x=860, rely=0.05)

        play_button = tk.Button(
            frame, text='PLAY', command=self._play
        )
        play_button.place(relheight=0.9, width=97, x=963, rely=0.05)

        self.volume = tk.IntVar(value=100)
        volume_slider = tk.Scale(
            frame, label='Volume', orient='horizontal', from_=0, to=100,
            variable=self.volume, length=182
        )
        volume_slider.place(relx=0.9)

        frame.place(relheight=0.1, relwidth=1, relx=0, rely=0.9)

    def _record(self) -> None:
        """Record user input and update the graph.
        
        Record using function from sounddevice library and mutate the
        signal attribute in signalobj to the newly recorded signal.
        """
        audio_signal_in = sd.rec(
            self.signalobj.duration.get() * sampling_rate, blocking=True
        )

        # Cast audio_signal_in from a 2d array to a 1d array.
        reduced_dim = np.zeros(self.signalobj.duration.get() * sampling_rate)
        for j in range(self.signalobj.duration.get() * sampling_rate):
            reduced_dim[j] = audio_signal_in[j][0]

        self.signalobj.signal = reduced_dim
        self.signalobj.plot_waveform()
        self.signalobj.plot_dft()


# Classes for individual effects?