import numpy as np
import mne

#ToDo: you can drop part of the signal in the middle, think about it

class Preprocessor(object):
    def __init__(self, segment, config):

        self.segment                = segment
        self.cropStartTime          = config.cropStartTime
        self.cropEndTime            = config.cropEndTime
        self.frequencyBandpass      = config.frequencyBandpass
        self.timeBandPassLow        = config.timeBandPassLow
        self.timeBandPassHigh       = config.timeBandPassHigh

        self.clean()


    def crop_start_end(self):
        # elimination of some artifacts
        newStart = int(self.cropStartTime * self.segment.duration)
        newEnd = int(self.cropEndTime * self.segment.duration)
        self.segment.signals = self.segment.signals[:, newStart * self.segment.sampling_freq: -newEnd * self.segment.sampling_freq]
        self.segment.duration = self.segment.duration - (newStart + newEnd)


    def apply_bandpass_frequency_domain(self):
        # Remove the power line frequency from the segment
        self.segment.signals = mne.filter.notch_filter(self.segment.signals,
                                                       self.segment.sampling_freq,
                                                       np.arange(self.frequencyBandpass,
                                                                 self.segment.sampling_freq / 2,
                                                                 self.frequencyBandpass),
                                                       verbose='error')

    def apply_bandpass_time_domain(self):
        #filter the signal in the band defines by low and high values
        self.segment.signals = mne.filter.filter_data(self.segment.signals,
                                                      self.segment.sampling_freq,
                                                      self.timeBandPassLow,
                                                      self.timeBandPassHigh,
                                                      verbose='error')

    def volts_to_microvolts(self):
        self.segment.signals *= 1000000


    def clean(self):
        self.crop_start_end()
        self.apply_bandpass_frequency_domain()
        self.apply_bandpass_time_domain()
        self.volts_to_microvolts()











