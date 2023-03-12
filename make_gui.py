import numpy as np

from scipy.fft import fft, fftfreq, fftshift
from scipy import signal

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import ttk

import sounddevice as sd

import filter_library

# sampling rate is globally fixed at the CD standard of 44_100 Hz
sampling_rate = 44_100

# sounddevice defaults for recording and playback
sd.default.samplerate = sampling_rate
sd.default.channels = 1


class GUI:

    def __init__(self) -> None:
        self.root = tk.Tk()

        self._set_window_params()
        
        # Set default recording duration and sampling times.
        self.duration = tk.IntVar(value=5)
        self.times = np.linspace(
            0, self.duration.get(), self.duration.get() * sampling_rate
            )
        # Intialize audio_signal attribute as the 0 function.
        self.audio_signal = np.zeros(self.duration.get() * sampling_rate)

        # Figures to hold f and F[f].
        self.fig_time = plt.figure()
        self.fig_freq = plt.figure()

        ###############################################################
        # Create notebook widget for time and frequency domain waveform
        # graphs.

        graph_notebook = ttk.Notebook(
            self.root
        )

        # Time domain canvas.
        canvas_frame_time = tk.Frame(
            graph_notebook
        )
        self.time_display = FigureCanvasTkAgg(
            self.fig_time, master=canvas_frame_time
            )
        self.time_display.get_tk_widget().pack()
        canvas_frame_time.pack()

        # Frequency domain canvas.
        canvas_frame_freq = tk.Frame(
            graph_notebook
        )
        self.freq_display = FigureCanvasTkAgg(
            self.fig_freq, master = canvas_frame_freq
        )
        self.freq_display.get_tk_widget().pack()
        canvas_frame_freq.pack()

        graph_notebook.add(canvas_frame_time, text='Time Domain')
        graph_notebook.add(canvas_frame_freq, text='Frequency Domain')
        
        graph_notebook.place(
            anchor='nw'
        )

        # Graph f and F[f] on the canvas(es).
        self._plot_waveform()
        self._plot_dft()
        
        ###############################################################
        # Frame for recording and playback related widgets.

        recording_frame = tk.Frame(
            self.root, borderwidth=2, relief='raised'
        )

        # Control recording duration.
        duration_slider = tk.Scale(
            recording_frame, label='Recording Length', orient='horizontal',
            from_=5, to=20, variable=self.duration, command=self._update_times,
            length=182
        )
        duration_slider.place(x=5)

        record_button = tk.Button(
            recording_frame, text='RECORD', command=self._record
        )
        record_button.place(relheight=0.9, width=97, x=860, rely=0.05)

        play_button = tk.Button(
            recording_frame, text='PLAY', command=self._play
        )
        play_button.place(relheight=0.9, width=97, x=963, rely=0.05)

        self.volume = tk.IntVar(value=100)
        volume_slider = tk.Scale(
            recording_frame, label='Volume', orient='horizontal',
            from_=0, to=100, variable=self.volume, length=182
        )
        volume_slider.place(relx=0.9)

        recording_frame.place(relheight=0.1, relwidth=1, relx=0, rely=0.9)

        ###############################################################
        # Labeled frame for all effect subframes.

        effects_frame = ttk.LabelFrame(
            self.root, text='Effects'
        )

        # Labeled subframe for delay effect and parameters.
        delay_frame = ttk.Labelframe(
            effects_frame, text='Delay'
        )

        delay_button = tk.Button(
            delay_frame, text='Apply Effect', command=self._delay
        )
        delay_button.pack()

        # Number of echoes for delay effect.
        self.num_echoes = tk.IntVar()
        echoes_slider = tk.Scale(
            delay_frame, variable=self.num_echoes, from_=0, to=8,
            orient='horizontal', label='Num echoes'
        )
        echoes_slider.pack(side='left')

        # Length of delay effect.
        self.len_delay = tk.DoubleVar()
        delay_slider = tk.Scale(
            delay_frame, variable=self.len_delay, from_=0.2, to=1.2,
            orient='horizontal', label='Len delay', resolution=0.05
        )
        delay_slider.pack(side='right')

        delay_frame.pack()

        # Labeled subframe for reverb effect and parameters.
        reverb_frame = ttk.Labelframe(
            effects_frame, text='Reverb'
        )

        reverb_button = tk.Button(
            reverb_frame, text='Apply Effect', command=self._reverb
        )
        reverb_button.pack()

        reverb_frame.pack()

        # Labeled subframe for flanger effect and parameters.
        flanger_frame = ttk.Labelframe(
            effects_frame, text='Flanger'
        )

        flanger_button = tk.Button(
            flanger_frame, text='Apply Effect', command=self._flanger
        )
        flanger_button.pack()

        # Select shape from 3 options.
        self.flange_shape = tk.StringVar()
        shape_button1 = ttk.Radiobutton(
            flanger_frame, text='Sin', variable=self.flange_shape, value='sin'
        )
        shape_button2 = ttk.Radiobutton(
            flanger_frame, text='Triangle', variable=self.flange_shape, 
            value='triangle'
        )
        shape_button3 = ttk.Radiobutton(
            flanger_frame, text='Sawtooth', variable=self.flange_shape,
            value='saw'
        )
        shape_button1.pack()
        shape_button2.pack()
        shape_button3.pack()

        # Control sweep.
        self.flange_sweep = tk.DoubleVar()
        sweep_slider = tk.Scale(
            flanger_frame, from_=0.1, to=0.33, resolution=0.01,
            variable=self.flange_sweep, orient='horizontal',
            label = 'Sweep'
        )
        sweep_slider.pack(side='right')

        # Control depth.
        self.flange_depth = tk.DoubleVar()
        depth_slider = tk.Scale(
            flanger_frame, from_=0.001, to=0.008, resolution=0.001,
            variable=self.flange_depth, orient='horizontal',
            label = 'Depth'
        )
        depth_slider.pack()

        flanger_frame.pack()

        effects_frame.place(relx=0.34, rely=0)


    def _quit(self) -> None:
        """Quit and destroy Tk window.
        
        The default root.quit method is not sufficient to halt the
        program because of some interaction with matplotlib, so we
        call both root.quit and root.destroy.
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
        
        # Set default window size to be maximized to screen dimensions on Linux.
        self.root.attributes('-zoomed', True)

    # def _set_pyplot_params(self) -> None:
    #     """Set parameters for the axes displayed on the figure canvas.
        
    #     Axes tick parameters, line properties, etc.. Just makes the
    #     constructor code less busy.
    #     """
    #     pass

    def _update_times(self, duration_str) -> None:
        """Update self.times to reflect a change in self.duration. """
        duration = int(duration_str)
        self.times = np.linspace(0, duration, duration * sampling_rate)

    def _record(self) -> None:
        """Record user input and update the graph.
        
        Calls the relevant function from sounddevice (using our
        defaults). Execution of the program is paused while the
        recording completes. After new data is written out to 
        `self.audio_signal`, `_plot_waveform` is called to update the
        graphed waveform on the figure canvas.
        """
        audio_signal_in = sd.rec(
            self.duration.get() * sampling_rate, blocking=True
        )

        # Cast audio_signal_in from a 2d array to a 1d array.
        # This is needed because all our filters operate on 1d arrays.
        reduced_dim = np.zeros(self.duration.get() * sampling_rate)
        for j in range(self.duration.get() * sampling_rate):
            reduced_dim[j] = audio_signal_in[j][0]

        self.audio_signal = reduced_dim
        self._plot_waveform()
        self._plot_dft()
    
    def _play(self) -> None:
        """Play back recorded signal. 
        
        Simply calls the relevant function from sounddevice.
        """
        # First modify the volume of the signal.
        playback_signal = self.volume.get() / 100 * self.audio_signal

        sd.play(playback_signal)

    def _plot_waveform(self) -> None:
        """Draw recorded signal as a waveform on the Tk figure canvas. 
        
        Clear existing axes and create a new axes object populated by a
        graph of the current audio_signal.
        """
        self.fig_time.clear()
        ax = self.fig_time.add_subplot(111)
        ax.set_title('Signal, Time Domain')

        ax.plot(self.times, self.audio_signal, color='orange')
        self.time_display.draw()

    def _plot_dft(self) -> None:
        """Graph the DFT of audio_signal.
        
        Plots the amplitude portion of the amplitude-phase form of the
        DFT on the figure canvas.
        """
        audio_signalft = fftshift(fft(self.audio_signal))
        freq = fftshift(fftfreq(self.times.shape[-1]))

        self.fig_freq.clear()
        ax = self.fig_freq.add_subplot(111)
        ax.set_title('Signal, Frequency Domain')

        ax.plot(freq, audio_signalft, color='green')
        self.freq_display.draw()

    ###################################################################
    # Wrapper methods for driving filter_library functions with Tk 
    # buttons.

    def _delay(self) -> None:
        """Apply a delay or echo effect to audio_signal.
        
        Calls the appropriate function from the filter library and match
        it with the relevant parameters set in the GUI.
        """
        delayed = filter_library.delay_effect(
            self.audio_signal, echoes=self.num_echoes.get(),
            delay=self.len_delay.get()
        )
        self.audio_signal = delayed
        self._plot_waveform()
        self._plot_dft()

    def _reverb(self) -> None:
        """Apply a reverb effect to audio_signal.
        
        Calls the delay function from filter library with parameters tuned
        differently to the _delay method.
        """
        reverbed = filter_library.delay_effect(
            self.audio_signal, echoes=10, delay=0.1
        )
        self.audio_signal = reverbed
        self._plot_waveform()
        self._plot_dft()

    def _flanger(self) -> None:
        """Apply a flanger effect to audio_signal.

        Call the appropriate function from the filter library and match
        it with the relevant parameters set in the GUI.
        """
        flanged = filter_library.flanger_effect(
            self.audio_signal, self.flange_depth.get(), 
            self.flange_sweep.get(), shape=self.flange_shape.get()
        )
        self.audio_signal = flanged
        self._plot_waveform()
        self._plot_dft()