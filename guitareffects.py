import numpy as np
from scipy import signal
from scipy.io import wavfile

class GuitarEffects:

    def uniform_distortion(self, input: np.array) -> np.array:
        """ Distort input signal by convolving against a uniform distribution. """
        dist = np.full(1000, 0.001)
        return signal.oaconvolve(input, dist)

    def gaussian_distortion(self, input: np.array) -> np.array:
        """ Distort input signal by convolving against a gaussian distribution. """
        pass

def main():
    
    effects = GuitarEffects()

    raw_input = wavfile.read('sin.wav')         # raw_input is a tuple with sampling rate at index 0, data at index 1, type at index 2
    waveform = raw_input[1]                     


if __name__ == '__main__':
    main()