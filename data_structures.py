import logging
import numpy as np
from scipy import signal


from functions import feature_frequency
from functions import feature_time



class DataWindower(object):
    def __init__(self, overlap, windowSizeSec, window='boxcar'):
        self.overlap = overlap / 100
        self.window = window
        self.windowSizeSec = windowSizeSec


    def apply_window(self, windows, window_size):
        """
        :param windows: the signals splitted into time windows
        :param window_size: the number of samples in the window
        :return: the windows weighted by the specified window function
        """
        windower = getattr(signal, self.window)
        window = windower(window_size)

        return windows * window


    def split(self, samples, samplingFreq):
        """
        :param rec: the recording object holding the signals and all information needed
        :return: the signals split into time windows of the specified size
        """
        window_size = int(samplingFreq * self.windowSizeSec)
        overlap_size = int(self.overlap * window_size)
        stride = window_size - overlap_size

        if stride == 0:
            logging.error("Time windows cannot have an overlap of 100%.")

        # written by robin tibor schirrmeister
        signal_crops = []
        for i_start in range(0, samples.shape[-1] - window_size + 1, stride):
            signal_crops.append(np.take(samples, range(i_start, i_start + window_size), axis=-1, ))


        return self.apply_window(np.array(signal_crops), window_size)





class Segment(object):

    def __init__(self, samplingFreq, nSamples, duration, timeSamples,
                 electrodes, label, fftSamples=None):

        self.samplingFreq = samplingFreq
        self.nSamples = nSamples
        self.duration = duration
        self.timeSamples = timeSamples
        self.windowedTimeSamples = []
        self.electrodeNames = electrodes
        self.label= label
        self.fftSamples = fftSamples
        self.fftExtractors = sorted([feat_func for feat_func in dir(feature_frequency) if not feat_func.startswith('_')])
        self.timeExtractors = sorted([feat_func for feat_func in dir(feature_time) if not feat_func.startswith('_')])

        windower = DataWindower(overlap=50, windowSizeSec=2)
        self.windowedTimeSamples = windower.split(self.timeSamples, self.samplingFreq)
        self.fftSamples = np.fft.rfft(self.windowedTimeSamples, axis=2)
