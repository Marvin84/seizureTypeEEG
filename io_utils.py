import logging
import pandas as pd
import mne




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

























