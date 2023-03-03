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
    `audioin`: np.ndarray
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
    
    The effect is achieved by convolving `audioin` with a Dirac comb
    that has been attenuated by a sharp decay function. To keep the
    operation from increasing (read: doubling) the duration, the result
    of the convolution is pruned back to the first n points using the
    `_trim_convolution` helper function.

    Parameters
    ----------
    audioin: np.ndarray
        The audio signal to which the echo effect will be added.

    echoes: int
        The number of echoes to add.

    delay: float
        The spacing between echoes in seconds.

    samplerate: int
        The sampling rate of the audio signal, defaults to CD standard.
    
    Returns
    -------
    np.ndarray
        The signal with echo added.
    """
    # Round delay to nearest sample number.
    delay = math.floor(delay * samplerate)

    # Each echo is a Dirac impulse with a decaying height.
    comb = np.zeros(len(audioin))
    for j in range(echoes + 1):
        # The argument of the decay function is normalized by
        # samplerate to make the decay a function of time rather
        # than sample number.
        if delay * j <= len(audioin):
            comb[delay * j] = math.exp(-j)

    # Calculate the (2n-1) point convolution.
    audioout = signal.fftconvolve(audioin, comb)

    # Prune the convolution to n points.
    audioout = _trim_convolution(audioout)

    return audioout

# todo: phaser, chorus, reverb, flanger, treble, bass, midrange