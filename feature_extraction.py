import numpy as np
import pandas as pd
import scipy

import pyeeg
from config import *


def bin_power(X, Band, Fs):
    """ taken from pyeeg lib and adapted since on cluster slicing failed through float indexing.
    :param X: 1d signal
    :param Band: frequency band
    :param Fs: sampling frequency
    :return: power and power ratio of frequency band
    """
    C = np.fft.fft(X)
    C = abs(C)
    Power = np.zeros(len(Band) - 1)
    for Freq_Index in range(0, len(Band) - 1):
        Freq = float(Band[Freq_Index])
        Next_Freq = float(Band[Freq_Index + 1])
        Power[Freq_Index] = sum(
            C[int(Freq / Fs * len(X)): int(Next_Freq / Fs * len(X))]
        )
    Power_Ratio = Power / sum(Power)
    return Power, Power_Ratio


def spectral_entropy(self, X, Band, Fs, Power_Ratio=None):
    """ taken from pyeeg lib and adapted to use self.bin_power since it returned nan
    :param X:
    :param Band:
    :param Fs:
    :param Power_Ratio:
    :return:
    """
    if Power_Ratio is None:
        Power, Power_Ratio = self.bin_power(X, Band, Fs)

    # added to catch crashes
    if len(Power_Ratio) == 1:
        return 0

    Spectral_Entropy = 0
    for i in range(0, len(Power_Ratio) - 1):
        Spectral_Entropy += Power_Ratio[i] * np.log(Power_Ratio[i])
    Spectral_Entropy /= np.log(
        len(Power_Ratio)
    )  # to save time, minus one is omitted
    return -1 * Spectral_Entropy


def compute_pyeeg_feats(segment):
    # these values are taken from the tuh paper
    TAU, DE, Kmax = 4, 10, 5
    pwrs, pwrrs, pfds, hfds, mblts, cmplxts, ses, svds, fis, hrsts = [], [], [], [], [], [], [], [], [], []
    dfas, apes = [], []

    for window_id, window in enumerate(segment.timeSamples):
        for window_electrode_id, window_electrode in enumerate(window):
            # taken from pyeeg code / paper
            electrode_diff = list(np.diff(window_electrode))
            M = pyeeg.embed_seq(window_electrode, TAU, DE)
            W = scipy.linalg.svd(M, compute_uv=False)
            W /= sum(W)

            power, power_ratio = bin_power(window_electrode, config_bands, segment.samplingFreq)
            pwrs.extend(list(power))
            # mean of power ratio is 1/(len(self.bands)-1)
            pwrrs.extend(list(power_ratio))

            pfd = pyeeg.pfd(window_electrode, electrode_diff)
            pfds.append(pfd)

            hfd = pyeeg.hfd(window_electrode, Kmax=Kmax)
            hfds.append(hfd)

            mobility, complexity = pyeeg.hjorth(window_electrode, electrode_diff)
            mblts.append(mobility)
            cmplxts.append(complexity)

            se = spectral_entropy(window_electrode,config_bands, segment.samplingFreq, power_ratio)
            ses.append(se)

            svd = pyeeg.svd_entropy(window_electrode, TAU, DE, W=W)
            svds.append(svd)

            fi = pyeeg.fisher_info(window_electrode, TAU, DE, W=W)
            fis.append(fi)

            # this crashes...
            # ape = pyeeg.ap_entropy(electrode, M=10, R=0.3*np.std(electrode))
            # apes.append(ape)

            # takes very very long to compute
            hurst = pyeeg.hurst(window_electrode)
            hrsts.append(hurst)

            # takes very very long to compute
            # dfa = pyeeg.dfa(electrode)
            # dfas.append(dfa)

    pwrs = np.asarray(pwrs).reshape(segment.timeSamples.shape[0], segment.timeSamples.shape[1], len(config_bands) - 1)
    pwrs = np.mean(pwrs, axis=0)

    pwrrs = np.asarray(pwrrs).reshape(segment.timeSamples.shape[0], segment.timeSamples.shape[1], len(config_bands) - 1)
    pwrrs = np.mean(pwrrs, axis=0)

    pfds = np.asarray(pfds).reshape(segment.timeSamples.shape[0], segment.timeSamples.shape[1])
    pfds = np.mean(pfds, axis=0)

    hfds = np.asarray(hfds).reshape(segment.timeSamples.shape[0], segment.timeSamples.shape[1])
    hfds = np.mean(hfds, axis=0)

    mblts = np.asarray(mblts).reshape(segment.timeSamples.shape[0], segment.timeSamples.shape[1])
    mblts = np.mean(mblts, axis=0)

    cmplxts = np.asarray(cmplxts).reshape(segment.timeSamples.shape[0], segment.timeSamples.shape[1])
    cmplxts = np.mean(cmplxts, axis=0)

    ses = np.asarray(ses).reshape(segment.timeSamples.shape[0], segment.timeSamples.shape[1])
    ses = np.mean(ses, axis=0)

    svds = np.asarray(svds).reshape(segment.timeSamples.shape[0], segment.timeSamples.shape[1])
    svds = np.mean(svds, axis=0)

    fis = np.asarray(fis).reshape(segment.timeSamples.shape[0], segment.timeSamples.shape[1])
    fis = np.mean(fis, axis=0)

    return list(pwrs.ravel()), list(pwrrs.ravel()), pfds, hfds, mblts, cmplxts, ses, svds, fis, apes, hrsts, dfas