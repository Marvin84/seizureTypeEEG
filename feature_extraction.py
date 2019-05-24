import numpy as np
import pandas as pd


from functions import feature_frequency
from functions import feature_time


class FeatureExtractor(object):

    def __init__(self, windowSize, overlap, fftExtractors, timeExtractors, electrodes, bands):

        self.windowSizeSec = 2
        self.windowSize = windowSize
        self.windowOverlap = overlap #already divided by 100
        self.bandOverlap = 0.5 # add the suggested band overlap of 50%
        self.overlapSize = int(overlap * windowSize)
        self.featureLabels = []
        self.fftExtractors = fftExtractors
        self.timeExtractors = timeExtractors
        self.electrodes = electrodes
        self.bands = bands
        self.features = {}




    def compute_mean_freq_features(self, freqFeatureName, segment):
        #ToDo: try also standard deviation
        """ Computes the feature values for a given recording. Computes the value the frequency bands as specified in
        band_limits. The values are mean over all time windows and channels
        :param freq_feat_name: the function name that should be called
        :param rec: the recording object holding the data and info
        :return: mean amplitudes in frequency bands over the different channels
        """
        func = getattr(feature_frequency, freqFeatureName)
        # amplitudes shape: windows x electrodes x frequencies
        amplitudes = np.abs(segment.fftSamples)
        windowSize = self.windowSizeSec * segment.samplingFreq
        freqBinSize = segment.samplingFreq / windowSize

        meanAmplitudes = []
        for i in range(len(self.bands) - 1):
            lower, upper = self.bands[i], self.bands[i+1]

            if i != 0:
                lower -= self.bandOverlap * (self.bands[i] - self.bands[i-1])
            if i != len(self.bands) - 2:
                upper += self.bandOverlap * (self.bands[i+2] - self.bands[i+1])

            lowerBin, upperBin = int(lower / freqBinSize), int(upper / freqBinSize)
            bandAmplitudes = amplitudes[:, :, lowerBin:upperBin]

            meanAmplitudeBands = func(bandAmplitudes, axis=2)
            meanAmplitudeWindows = np.mean(meanAmplitudeBands, axis=0)
            meanAmplitudes.extend(list(meanAmplitudeWindows))

        return meanAmplitudes



    def get_freq_feature_labels(self):
        for fExt in self.fftExtractors:
            for band_id, band in enumerate(self.bands[:-1]):
                for electrode in self.electrodes:
                    label = '_'.join(['fft', fExt, str(band) + '-' + str(self.bands[band_id + 1]) + 'Hz',
                                      str(electrode)])
                    self.featureLabels.append(label)

    def get_time_feature_labels(self):
        for tExt in self.timeExtractors:
            for electrode in self.electrodes:
                label = '_'.join(['time', tExt, str(electrode)])
                self.featureLabels.append(label)

    def rolling_to_windows(self, features):
        """ This should be used to transform the results of the rolling operation of pandas to window values.
        beware! through ".diff" in pandas feature computation, a row of nan is inserted to the rolling feature.
        :param features: feature computation achieved through pandas.rolling()
        :return: rolling feature sliced at the window locations
        """
        return features[self.windowSize - 1::self.windowSize - self.overlapSize]

    def extract_features_in_freq(self, segment):
        for freqFeatureName in self.fftExtractors:
            features = self.compute_mean_freq_features(freqFeatureName, segment)
            label =  '_'.join(['fft', freqFeatureName])
            self.features[label] = features

    def extract_features_in_time(self, segment):
        for timeFeatureName in self.timeExtractors:
            func = getattr(feature_time, timeFeatureName)
            allFeatures = func(pd.DataFrame(segment.timeSamples.T), self.windowSize)
            featSlidingWindows = self.rolling_to_windows(allFeatures)
            meanValues = np.mean(featSlidingWindows, axis=0)
            label = '_'.join(['time', timeFeatureName])
            self.features[label] = meanValues


