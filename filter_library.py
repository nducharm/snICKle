import math

import numpy as np

from scipy import signal

def _trim_convolution(audioin: np.ndarray) -> np.ndarray:
    """Trim off the back half of an array.

    When you convolve two n-point arrays the result is a single (2n-1)
    point array. For delay effects, if you want to keep the duration
    of the audio signal the same, you need to retain the first n points
    of the resulting signal rather. This helper function trims a 2n-1
    point array, keeping only the first n points.

    Parameters
    ----------
    audioin: np.ndarray
        A 1-dimensional (2n-1) point array.

    Returns
    -------
    np.ndarray
        The first n points of `audioin`.
    """
    length = len(audioin)
    half_length = (length + 1) // 2

    index_list = [x for x in range(half_length, length)]

    trimmed = np.delete(audioin, index_list)

    return trimmed

def delay_effect(
        audioin: np.ndarray, echoes: int, delay: float,
        samplerate: int = 44_100
    ) -> np.ndarray:
    """"Add one or more echoes to a signal without increasing duration.
    
    The effect is achieved by convolving x[n] with a Dirac comb D[n]
    that has been attenuated by a sharp decay function. To keep the
    operation from increasing (read: doubling) the duration, the result
    of the convolution is pruned back to the first n points using the
    `_trim_convolution` helper function.

    Parameters
    ----------
    audioin: np.ndarray
        Audio input, x[n].

    echoes: int
        The number of echoes to add.

    delay: float
        The spacing between echoes in seconds.

    samplerate: int
        The sampling rate in Hz of the input signal.
    
    Returns
    -------
    np.ndarray
        First n points of (x * D)[n].
    """
    # Convert delay from seconds to samples.
    delay = math.floor(delay * samplerate)

    # Each echo is a Dirac impulse with a decaying height.
    comb = np.zeros(len(audioin))
    for j in range(echoes + 1):
        if delay * j <= len(audioin):
            comb[delay * j] = math.exp(-j)

    # Calculate the (2n-1) point convolution.
    audioout = signal.fftconvolve(audioin, comb)

    # Prune the convolution to n points.
    audioout = _trim_convolution(audioout)

    return audioout

def flanger_effect(
        audioin: np.ndarray, depth: float, sweep: float = 1,
        samplerate: int = 44_100, shape: str = 'triangle'
    ) -> np.ndarray :
    """Overlap a signal with a time-varying delayed copy.
    
    A flanger is a delay that varies with time according to some 
    low-frequency wave. The output should look like y[n] = x[n] + 
    x[n - M[n]] where M[n] is the time varying delay parameter.

    Parameters
    ----------
    audioin: np.ndarray
        Audio input, x[n].

    depth: float
        Amplitude of M[n].

    sweep: float
        Frequency of M[n].

    samplerate: int
        The sampling rate in Hz of the input signal.

    shape: str
        The type of function M[n] will be. May be 'triangle', 'sin' or
        'saw'.

    Returns
    -------
    np.ndarray
        x[n] + x[n - M[n]]
    """
    # Input sanitization for shape.
    shapes = ['triangle', 'sin', 'saw']
    if shape not in shapes:
        raise ValueError('Invalid shape. Expected "triangle", "sin" or "saw".')

    # Convert depth from seconds into samples.
    depth= math.floor(depth * samplerate)

    length = len(audioin)
    sampletimes = np.linspace(0, length // samplerate, length)
    
    # Generate the delay wave.
    if shape == 'triangle':
        delay_wave = depth + depth * signal.sawtooth(
            2 * np.pi * sampletimes * sweep, 0.5
        )
    elif shape == 'saw':
        delay_wave = depth + depth * signal.sawtooth(
            2 * np.pi * sampletimes * sweep
        )
    elif shape == 'sin':
        delay_wave = depth + depth * np.sin(
            2 * np.pi * sampletimes * sweep
        )

    # At each index j, the signal out should be x[j] + x[j - M[j]].
    audioout = np.zeros(length)
    for j in range(length):
        # If-elif-else block handles out of bounds.
        if j - delay_wave[j] < 0:
            audioout[j] = audioin[j] + audioin[0]
        # Pretty sure this isn't possible, can remove this elif clause.
        elif j - delay_wave[j] >= length:
            audioout[j] = audioin[j] + audioin[length - 1]
        else:
            # delay_wave is currently integer values stored as floats.
            audioout[j] = audioin[j] + audioin[j - int(delay_wave[j])]

    return audioout
        

# todo: phaser, chorus, treble, bass, midrange