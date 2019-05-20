
import numpy as np
import nme
from scipy import signal


class DataSplitter(object):
    """
    """

    @staticmethod
# ______________________________________________________________________________________________________________________
    def get_supported_windows():
        return WINDOWS


# ______________________________________________________________________________________________________________________
    def windows_weighted(self, windows, window_size):
        """ weights the splitted signal by the specified window function
        :param windows: the signals splitted into time windows
        :param window_size: the number of samples in the window
        :return: the windows weighted by the specified window function
        """
        method_to_call = getattr(signal, self.window)
        window = method_to_call(window_size)

        return windows * window

# ______________________________________________________________________________________________________________________
    def split(self, signals, sampling_freq):
        """ written by robin schirrmeister, adapted by lukas gemein
        :param rec: the recording object holding the signals and all information needed
        :return: the signals split into time windows of the specified size
        """
        window_size = int(sampling_freq * self.window_size_sec)
        overlap_size = int(self.overlap * window_size)
        stride = window_size - overlap_size

        if stride == 0:
            logging.error("Time windows cannot have an overlap of 100%.")

        # written by robin tibor schirrmeister
        signal_crops = []
        for i_start in range(0, signals.shape[-1] - window_size + 1, stride):
            signal_crops.append(np.take(signals, range(i_start, i_start + window_size), axis=-1, ))

        return self.windows_weighted(np.array(signal_crops), window_size)

# ______________________________________________________________________________________________________________________
    def __init__(self, overlap=50, window='boxcar', window_size_sec=2):
        self.overlap = overlap/100
        self.window = window
        self.window_size_sec = window_size_sec






class EdfFile(object):

    """
    This is a container class for reading an edf file and storing the relevant information of an EEG recording

    """

    def __init__(self, filename):

        self.filename = filename
        self.labelInfoList = []

        self.read_edf_file()



        """
        self.signals = signals
        self.signal_ft = signals_ft
        self.signals_complete = signals_complete
        """

    def getLabelAndTimeCuts(self):
        returnList = []
        with open(self.filename + ".tse") as file:
            for line in file:
                if len(line.split()) == 4:
                    returnList.append(line.split()[:-1])
        return returnList


    def read_edf_file(self):

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
        self.electrodeNames = self.rawEdf.ch_names
        self.duration = self.nSamples / max(self.samplingFreq, 1)

        labelList = self.getLabelAndTimeCuts()
        for ele in labelList:
            ele[2] = labelList[ele[2]]
            self.labelInfoList.append(ele)

    def filterChannels(rec_channels, wanted_elecs):

        selected_ch_names = []
        for wanted_part in wanted_elecs:
            wanted_found_name = []
            for ch_name in rec_channels:
                if ' ' + wanted_part + '-' in ch_name:
                    wanted_found_name.append(ch_name)
            assert len(wanted_found_name) == 1
            selected_ch_names.append(wanted_found_name[0])
        return selected_ch_names











    def init_processing_units(self):
        self.splitter = DataSplitter(overlap = 50, window_size_sec=2)
        # self.feature_generator = feature_generator.FeatureGenerator(domain=cmd_args.domain, bands=cmd_args.bands,
        #                                                            window_size_sec=2,
        #                                                            overlap=50,
        #                                                           electrodes=wanted_elecs)


class Segment(object):

    def __init__(self, sampling_freq, n_samples, signal_names, duration, label,
                 signals, signals_ft=None):

        self.sampling_freq = sampling_freq
        self.n_samples = n_samples
        self.signal_names = signal_names
        self.duration = duration
        self.signals = signals
        self. label= label
        self.signals_ft = signals_ft