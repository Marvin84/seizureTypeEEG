import logging
import nme
import numpy as np
import pandas as pd
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

# ______________________________________________________________________________________________________________________







class EdfFile(object):

    """
    This is a container class for reading an edf file and storing the relevant information of an EEG recording

    """

    def __init__(self, filename, wantedElectrodes):

        self.filename = filename
        self.electrodeNames = []
        self.labelInfoList = []



        self.read_edf_file()
        self.set_edf_channels(wantedElectrodes)




        """

        self.signal_ft = signals_ft
        self.signals_complete = signals_complete
        """

    def get_label_and_time_cuts(self):
        returnList = []
        with open(self.filename + ".tse") as file:
            for line in file:
                if len(line.split()) == 4:
                    returnList.append(line.split()[:-1])
        return returnList


    def read_edf_file(self, labels):

        self.edfPath = self.filename + ".edf"
        try:
            self.rawEdf = mne.io.read_raw_edf(self.filename + ".edf", verbose='error')

        except ValueError:
            return

        sampling_frequency = int(self.rawEdf.info['sfreq'])
        if sampling_frequency < 10:
            return
        else: self.samplingFreq = sampling_frequency

        self.nSamples       = self.rawEdf.n_times
        self.allElectrodes = self.rawEdf.ch_names
        self.duration = self.nSamples / max(self.samplingFreq, 1)

        labelList = self.get_label_and_time_cuts()
        for ele in labelList:
            ele[2] = labelList[ele[2]]
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



















