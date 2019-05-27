import logging
import numpy as np
import pandas as pd
import mne
from scipy import signal

from functions import feature_frequency
from functions import feature_time


class EdfFile(object):
    """
    This is a container class for reading an edf file and storing the relevant information of an EEG recording

    """

    def __init__(self, filename, wantedElectrodes, classes):

        self.filename       = filename
        self.electrodeNames = []
        self.labelInfoList  = []
        self.edfPath        = None
        self.rawEdf         = None
        self.nSamples       = None
        self.duration       = None
        self.timeSamples    = []

        self.read_edf_file(classes)
        self.set_edf_channels(wantedElectrodes)
        self.load_data_samples_for_electrodes()

    def get_label_and_time_cuts(self):
        returnList = []
        with open(self.filename + ".tse") as file:
            for line in file:
                if len(line.split()) == 4:
                    returnList.append(line.split()[:-1])
        return returnList

    def read_edf_file(self, classes):

        self.edfPath = self.filename + ".edf"
        try:
            self.rawEdf = mne.io.read_raw_edf(self.filename + ".edf", verbose='error')
        except ValueError:
            return

        sampling_frequency = int(self.rawEdf.info['sfreq'])
        if sampling_frequency < 10:
            return
        else:
            self.samplingFreq = sampling_frequency

        self.nSamples = self.rawEdf.n_times
        self.allElectrodes = self.rawEdf.ch_names
        self.duration = self.nSamples / max(self.samplingFreq, 1)

        labelList = self.get_label_and_time_cuts()
        for ele in labelList:
            ele[2] = classes[ele[2]]
            self.labelInfoList.append(ele)

    def set_edf_channels(self, wantedElectrods):
        for electrode in wantedElectrods:
            for edfElectrode in self.allElectrodes:
                if ' ' + electrode + '-' in edfElectrode:
                    self.electrodeNames.append(edfElectrode)

    def load_data_samples_for_electrodes(self):

        self.rawEdf.load_data()
        samples = self.rawEdf.get_data()

        data = pd.DataFrame(index=range(self.nSamples), columns=self.electrodeNames)
        for electrode in self.electrodeNames:
            data[electrode] = samples[list(self.allElectrodes).index(electrode)]

        self.timeSamples = data.values.T


class Segment(object):

    def __init__(self, samplingFreq, nSamples, duration, timeSamples,
                 electrodes, label, fftSamples=None, windowType='boxcar'):
        self.samplingFreq = samplingFreq
        self.nSamples = nSamples
        self.duration = duration
        self.timeSamples = timeSamples
        self.windowedTimeSamples = []
        self.electrodeNames = electrodes
        self.label = label
        self.fftSamples = fftSamples


        windower = DataWindower(windowType, windowSizeSec=2, overlap=50)
        self.windowedTimeSamples = windower.split(self.timeSamples, self.samplingFreq)
        self.fftSamples = np.fft.rfft(self.windowedTimeSamples, axis=2)


class DataWindower(object):
    def __init__(self, windowType, windowSizeSec, overlap ):

        self.windowType = windowType
        self.overlap = round(float(overlap / 100), 2)
        self.windowSizeSec = windowSizeSec

    def apply_window(self, windows, window_size):
        """
        :param windows: the signals splitted into time windows
        :param window_size: the number of samples in the window
        :return: the windows weighted by the specified window function
        """
        windower = getattr(signal, self.windowType)
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
        print("extractinf features in freq for segment with label", segment.label)
        featuresDict = {}
        for freqFeatureName in self.fftExtractors:
            features = self.compute_mean_freq_features(freqFeatureName, segment)
            label =  '_'.join(['fft', freqFeatureName])
            featuresDict[label] = features
        return featuresDict

    def extract_features_in_time(self, segment):
        featuresDict = {}
        for timeFeatureName in self.timeExtractors:
            func = getattr(feature_time, timeFeatureName)
            allFeatures = func(pd.DataFrame(segment.timeSamples.T), self.windowSize)
            featSlidingWindows = self.rolling_to_windows(allFeatures)
            meanValues = np.mean(featSlidingWindows, axis=0)
            label = '_'.join(['time', timeFeatureName])
            featuresDict[label] = meanValues.values

        return featuresDict