import math

import numpy as np

from scipy import signal
from scipy.fft import fft, ifft

def _trim_convolution(audioin: np.ndarray) -> np.ndarray:
    """Trim off the back half of an array.

    When you convolve two n-point arrays the result is a single (2n-1)
    point array. For delay effects, if you want to keep the duration
    of the audio signal the same, you need to retain the first n points
    of the resulting signal. Thuslywise, this helper function trims a 
    (2n-1) point array, keeping only the first n points.

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
    _trim_convolution helper function.

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

def _low_frequency_oscillator(
        amplitude: float, freq: float, shape: str, length: int,
        samplerate: int = 44_100 
    ) -> np.ndarray:
    """Generate a low frequency oscillator.
    
    Generate a wave, one of three types: sawtooth, triangle or sine.
    The oscillator should output a sample number, since it will be used
    to delay signals (so you can think of the output as being time, 
    which we then convert to samples). This is a helper function for 
    both the flanger and chorus effects.

    Parameters
    ----------
    amplitude: float
        Amplitude of the oscillator.

    freq:
        Frequency of the oscillator.

    shape:
        Type of oscillator. 'sin', 'triangle' or 'saw'.

    length:
        Number of samples in the oscillator.

    samplerate:
        A sampling rate determining the conversion rate from samples
        (length) to seconds.

    Return
    ------
    np.ndarray
        The infamous oscillator.
    """
    # Input sanitization for shape parameter.
    shapes = ['triangle', 'sin', 'saw']
    if shape not in shapes:
        raise ValueError(
            'Invalid shape. Expected "triangle", "sin" or "saw".'
        )

    # LFO should output a sample number, so convert amplitude to a
    # sample number.
    amplitude = math.floor(amplitude * samplerate)

    # Generate the LFO.
    sampletimes = np.linspace(0, length // samplerate, length)
    if shape == 'triangle':
        lfo = amplitude + amplitude * signal.sawtooth(
            2 * np.pi * sampletimes * freq, 0.5
        )
    elif shape == 'saw':
        lfo = amplitude + amplitude * signal.sawtooth(
            2 * np.pi * sampletimes * freq
        )
    elif shape == 'sin':
        lfo = amplitude + amplitude * np.sin(
            2 * np.pi * sampletimes * freq
        )
    
    return lfo

def flanger_effect(
        audioin: np.ndarray, depth: float, sweep: float,
        shape: str = 'triangle'
    ) -> np.ndarray :
    """Overlap a signal with a time-varying delayed copy.
    
    A flanger is a delay that varies with time according to some 
    low-frequency oscillator (LFO) M[n]. The output should look like
    y[n] = x[n] + x[n - M[n]]. M[n] is constructed with the
    _low_frequency_oscillator helper function.

    Parameters
    ----------
    audioin: np.ndarray
        Audio input, x[n].

    depth: float
        Amplitude of M[n].

    sweep: float
        Frequency of M[n].

    shape: str
        The type of oscillator M[n] will be. May be 'triangle', 'sin'
        or 'saw'.

    samplerate: int
        The sampling rate in Hz of the input signal.

    Returns
    -------
    np.ndarray
        y[n] = x[n] + x[n - M[n]]
    """
    length = len(audioin)

    # Call helper function to build M[n].
    delay_lfo = _low_frequency_oscillator(depth, sweep, shape, length)

    # At each index j, the signal out should be x[j] + x[j - M[j]].
    audioout = np.zeros(length)
    for j in range(length):
        # If-else block handles out of bounds.
        if j - delay_lfo[j] < 0:
            audioout[j] = audioin[j] + audioin[0]
        else:
            # delay_lfo is currently integer values stored as floats.
            audioout[j] = audioin[j] + audioin[j - int(delay_lfo[j])]

    return audioout

def chorus_effect(
        audioin: np.ndarray, voices: int, mode: str, depth: float, 
        shape: str = 'triangle', **sweepargs
    ) -> np.ndarray:
    """Overlap a signal with flanged copies.
    
    Produces the effect of multiple sources of sound, all mutually
    slightly out of sync pitch-wise. The output may be written
    y[n] = 1/N(x[n] + x[n - M_1[n]] + ... + x[n - M_N[n]]) where N
    is the number of copies of x[n] (voices) and M_j[n] is the j-th 
    LFO used to modulate the phase of x[n]. Again the LFOs are built
    using the _low_frequency_oscillator helper function.

    Parameters
    ----------

    audioin: np.ndarray
        Audio input, x[n].

    voices: int
        N, the number of modulated copies of the signal.

    mode: str
        'deterministic' or 'gaussian'. Determines how the sweep of the
        LFOs are generated -- 'deterministic' gives sweeps that are
        multiples of a base sweep, 'gaussian' draws sweeps randomly
        from a Gaussian distribution.

    maxsweep: float
        'deterministic' parameter, determines the base shift.

    sweepmean: float
        'gaussian' parameter, determines the mean of the Gaussian to be
        sampled from.

    sweepsd: float
        'gaussian' parameter, determines the std dev of the Gaussian to
        be sampled from.

    depth: float
        Shared amplitude of the LFOs.

    shape: str
        Type of oscillator the LFOs will be. 'sin', 'triangle', 'saw'.

    Returns
    -------
    np.ndarray
        y[n] = 1/N(x[n] + x[n - M_1[n]] + ... + x[n - M_N[n]])
    """
    # Input sanitization for mode parameter.
    modes = ['deterministic', 'gaussian']
    if mode not in modes:
        raise ValueError('Invalid mode. Expected "deterministic" or "gaussian".')

    if mode == 'deterministic':
        # Fetch kwargs.
        maxsweep = sweepargs['maxsweep']
        # Build vector of sweeps.
        sweep_vector = np.linspace(0, maxsweep, voices)
    elif mode == 'gaussian':
        # Fetch kwargs.
        sweepmean, sweepsd = sweepargs['sweepmean'], sweepargs['sweepsd']
        sweep_vector = np.random.normal(sweepmean, sweepsd, voices)

    # Build LFOs and add them to output.
    length = len(audioin)
    lfo_vector = [None] * voices
    for k, sweep in enumerate(sweep_vector):
        lfo_vector[k] = _low_frequency_oscillator(
            depth, sweep, shape, length
        )

    audioout = np.zeros(length)

    # Might be worth packaging this up as a helper function.
    for lfo in lfo_vector:
        for j in range(length):
            if j - lfo[j] < 0:
                audioout[j] = audioin[j] + audioin[0]
            else:
                audioout[j] = audioin[j] + audioin[j - int(lfo[j])]

    return audioout

def phaser_effect(
        audioin: np.ndarray, shift: int, **parameters
    ) -> np.ndarray:
    """Phase shift certain frequency bands."""
    # Bank frequency bands and phase shift band proportionally to the
    # maximum frequency in each band. Run this process across multiple
    # layers of filtering, 1 to 32.
    return

# todo: phaser, treble, bass, midrange