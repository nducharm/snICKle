import numpy as np

from scipy import signal
from scipy.io import wavfile


class GuitarEffects:

    def uniform_distortion(self, input: np.array) -> np.array:
        """ Convolution filter against a uniform distribution. """
        dist = np.full(1000, 0.001)
        return signal.oaconvolve(input, dist)

    def gaussian_distortion(self, input: np.array) -> np.array:
        """ Convolution filter against a gaussian distribution. """
        pass

    def fuzz_distortion(self, input: np.array) -> np.array:
        """ Nonlinear filter simulating an analog fuzz effect. """
        pass

    def overdrive_distortion(self, input: np.array) -> np.array:
        """ Filter simulating the effect of an overdriven tube amp. """
        pass

    def phaser(self, input: np.array) -> np.array:
        pass

    def delay(self, input: np.array) -> np.array:
        pass

    def reverb(self, input: np.array) -> np.array:
        pass
    
    def chorus(self, input: np.array) -> np.array:
        pass

def main():
    
    effects = GuitarEffects()

    raw_input = wavfile.read('sin.wav')         # raw_input is a tuple with sampling rate at index 0, data at index 1, type at index 2
    waveform = raw_input[1]                     


if __name__ == '__main__':
    main()