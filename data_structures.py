import logging
import numpy as np
import pandas as pd
import mne
from scipy import signal
import csv

from functions import feature_frequency
from functions import feature_time
from feature_extraction import *
from config import *


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
            #ele[2] = classes[ele[2]]
            #ToDo: decides which label you wanna include
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
                 electrodes, label, preprocessor, fftSamples=None, windowType='boxcar'):
        self.samplingFreq = samplingFreq
        self.nSamples = nSamples
        self.duration = duration
        self.timeSamples = timeSamples
        self.windowedTimeSamples = []
        self.electrodeNames = electrodes
        self.label = label
        self.fftSamples = fftSamples

        self.clean_timeSamples(preprocessor)
        windower = DataWindower(windowType, windowSizeSec=config_windowSizeSec, overlap=config_overlap*100)
        self.windowedTimeSamples = windower.split(self.timeSamples, self.samplingFreq)
        self.fftSamples = np.fft.rfft(self.windowedTimeSamples, axis=2)

    def clean_timeSamples(self, preprocessor):
        if preprocessor != None:
            preprocessor.clean(self)


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

    def __init__(self, windowSizeSec, windowSize, overlap, fftExtractors, timeExtractors, electrodes, bands):

        self.windowSizeSec      = windowSizeSec
        self.windowSize         = windowSize
        self.windowOverlap      = overlap                       #already divided by 100
        self.bandOverlap        = 0.5                           # add the suggested band overlap of 50%
        self.overlapSize        = int(overlap * windowSize)
        self.fftExtractors      = fftExtractors
        self.timeExtractors     = timeExtractors
        self.electrodes         = electrodes
        self.bands              = bands
        self.pyeegFeatureNames  = self.get_pyeeg_feature_names()
        self.features           = {"label":[]}



    def get_pyeeg_feature_names(self):
        pyeeg_freq_feats = ["pwr", "pwrr"]
        pyeeg_time_feats = ["pfd", "hfd", "mblt", "cmplxt", "se", "svd", "fi"]  # , "ape", "hrst", "dfa"]
        return sorted(pyeeg_freq_feats + pyeeg_time_feats)


    def set_freq_feature_with_label(self, funcName, bandLowId, bandHighId, featureVector):
        #receiving for a specific band a list of mean values of length of number of electrodes
        for index, electrode in enumerate(self.electrodes):
            label = '_'.join(['fft',
                              funcName,
                              str(bandLowId) + '-' + str(bandHighId) + 'Hz',
                              electrode])
            if label not in self.features:
                self.features[label] = []
            self.features[label].append(featureVector[index])


    def set_time_feature_labels(self, funcName, featureVector):
        # receiving list of mean values of length of number of electrodes
        for index, electrode in enumerate(self.electrodes):
            label = '_'.join(['time', funcName, str(electrode)])
            if label not in self.features:
                self.features[label] = []
            self.features[label].append(featureVector[index])


    def compute_mean_freq_features(self, freqFeatureName, segment):
        #ToDo: try also standard deviation
        """ Computes the feature values for a given recording. Computes the value the frequency bands as specified in
        band_limits. The values are mean over all time windows and channels
        :param freq_feat_name: the function name that should be called
        :param rec: the recording object holding the data and info
        """
        func = getattr(feature_frequency, freqFeatureName)
        # amplitudes shape: windows x electrodes x frequencies
        amplitudes = np.abs(segment.fftSamples)
        windowSize = self.windowSizeSec * segment.samplingFreq
        freqBinSize = segment.samplingFreq / windowSize


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

            self.set_freq_feature_with_label(freqFeatureName, self.bands[i], self.bands[i+1], meanAmplitudeWindows)




    def rolling_to_windows(self, features):
        """ This should be used to transform the results of the rolling operation of pandas to window values.
        beware! through ".diff" in pandas feature computation, a row of nan is inserted to the rolling feature.
        :param features: feature computation achieved through pandas.rolling()
        :return: rolling feature sliced at the window locations
        """
        return features[self.windowSize - 1::self.windowSize - self.overlapSize]

    def extract_features_in_freq(self, segment):
        for freqFeatureName in self.fftExtractors:
            self.compute_mean_freq_features(freqFeatureName, segment)

    def extract_features_in_time(self, segment):
        for timeFeatureName in self.timeExtractors:
            func = getattr(feature_time, timeFeatureName)
            allFeatures = func(pd.DataFrame(segment.timeSamples.T), self.windowSize)
            featSlidingWindows = self.rolling_to_windows(allFeatures)
            meanValues = np.mean(featSlidingWindows, axis=0)
            self.set_time_feature_labels(timeFeatureName, meanValues.values)



    def extract_pyeeg_features(self, segment):
        pwrs, pwrrs, pfds, hfds, mblts, cmplxts, ses, svds, fis, apes, hrsts, dfas = compute_pyeeg_feats(rec)

        self.features.extend(pwrs)
        self.features.extend(pwrrs)
        self.features.extend(pfds)
        self.features.extend(hfds)
        self.features.extend(mblts)
        self.features.extend(cmplxts)
        self.features.extend(ses)
        self.features.extend(svds)
        self.features.extend(fis)


    def extract_features_from_segment(self, segment):
        self.extract_features_in_freq(segment)
        self.extract_features_in_time(segment)
        self.features["label"].append(segment.label)


    def extract_features_from_segments(self, listOfSegments):
        print("here")
        for s in listOfSegments:
            print("extracting from segment", listOfSegments.index(s))
            self.extract_features_from_segment(s)


    def write_features_to_csv(self, filename):
        n = len(self.features[self.featureLabels[0]])
        features = []
        labels = []
        labels.extend(self.get_freq_feature_labels())
        labels.extend(self.get_time_feature_labels())
        labels.append("label")
        features.append(labels)
        for i in range(n):
            f = []
            for feat in labels:
                f.extend(self.features[feat][i])
            features.append(f)


        with open('.'.join([filename, "csv"]), 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(features)
