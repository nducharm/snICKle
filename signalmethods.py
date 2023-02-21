import numpy as np

from scipy.io import wavfile


def main():

    frequencies = [82.41, 123.47, 164.81, 207.65, 246.94, 329.64]    # Hz
    sampling_rate = 44_100    # Hz
    duration = 5    # seconds

    times = np.linspace(0, duration, sampling_rate * duration)      # sample times
    waveform = np.zeros(sampling_rate * duration)               # vector to hold cosine wave

    for frequency in frequencies:
        waveform += 2500 * np.cos(times * frequency * 2 * np.pi)

    wavfile.write('sin.wav', sampling_rate, waveform.astype(np.dtype('i2')))

if __name__ == "__main__":
    main()