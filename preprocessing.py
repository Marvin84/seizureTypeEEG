import numpy as np
import mne

#ToDo: you can drop part of the signal in the middle, think about it

class Preprocessor(object):
    def __init__(self, cropStartTime, cropEndTime, frequencyBandpass, timeBandPassLow, timeBandPassHigh):


        self.cropStartTime          = cropStartTime
        self.cropEndTime            = cropEndTime
        self.frequencyBandpass      = frequencyBandpass
        self.timeBandPassLow        = timeBandPassLow
        self.timeBandPassHigh       = timeBandPassHigh




    def crop_start_end(self):
        # elimination of some artifacts
        newStart = self.cropStartTime * self.segment.duration
        newEnd = self.cropEndTime * self.segment.duration
        self.segment.timeSamples = self.segment.timeSamples[:, int(newStart * self.segment.samplingFreq):
        -int(newEnd * self.segment.samplingFreq)]
        self.segment.duration = self.segment.duration - (newStart + newEnd)




    def apply_bandpass_frequency_domain(self):
        # Remove the power line frequency from the self.segment
        self.segment.timeSamples = mne.filter.notch_filter(self.segment.timeSamples,
                                                       self.segment.samplingFreq,
                                                       np.arange(self.frequencyBandpass,
                                                                 self.segment.samplingFreq / 2,
                                                                 self.frequencyBandpass),
                                                       verbose='error')



    def apply_bandpass_time_domain(self):
        #filter the signal in the band defines by low and high values
        self.segment.timeSamples = mne.filter.filter_data(self.segment.timeSamples,
                                                      self.segment.samplingFreq,
                                                      self.timeBandPassLow,
                                                      self.timeBandPassHigh,
                                                      verbose='error')



    def volts_to_microvolts(self):
        self.segment.timeSamples *= 1000000




    def clean(self, segment):
        self.segment = segment
        self.crop_start_end()
        self.apply_bandpass_frequency_domain()
        self.apply_bandpass_time_domain()
        self.volts_to_microvolts()
        return self.segment











