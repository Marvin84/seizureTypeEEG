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



    def crop_start_end(self, segment):
        # elimination of some artifacts
        newStart = int(self.cropStartTime * segment.duration)
        newEnd = int(self.cropEndTime * segment.duration)
        segment.timeSamples = segment.timeSamples[:, newStart * segment.samplingFreq: -newEnd * segment.samplingFreq]
        segment.duration = segment.duration - (newStart + newEnd)
        return segment



    def apply_bandpass_frequency_domain(self, segment):
        # Remove the power line frequency from the segment
        segment.timeSamples = mne.filter.notch_filter(segment.timeSamples,
                                                       segment.samplingFreq,
                                                       np.arange(self.frequencyBandpass,
                                                                 segment.samplingFreq / 2,
                                                                 self.frequencyBandpass),
                                                       verbose='error')
        return segment


    def apply_bandpass_time_domain(self, segment):
        #filter the signal in the band defines by low and high values
        segment.timeSamples = mne.filter.filter_data(segment.timeSamples,
                                                      segment.samplingFreq,
                                                      self.timeBandPassLow,
                                                      self.timeBandPassHigh,
                                                      verbose='error')
        return segment


    def volts_to_microvolts(self, segment):
        segment.timeSamples *= 1000000
        return segment



    def clean(self, segment):

        croppedSeg = self.crop_start_end(segment)
        bandFrequSeg = self.apply_bandpass_frequency_domain(croppedSeg)
        bandTimeSeg = self.apply_bandpass_time_domain(bandFrequSeg)
        cleanedSegment = self.volts_to_microvolts(bandTimeSeg)
        return cleanedSegment











