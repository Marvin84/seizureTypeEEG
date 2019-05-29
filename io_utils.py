import logging
import pandas as pd
import mne


from data_structures import *
from preprocessing import *
from config import *




def get_all_edf_files(filenames, wantedElectrodes, classes):
    """

    :param filenames: the names of the files without the extension
    :param wantedElectrodes: the electrodes that are to be included for the feature extraction
    :param classes: the seizure classes
    :return: the list of all edfFile objects
    """
    edfFiles = []
    for index, fName in enumerate(filenames.keys()):
        print("working on the recording ", str(index) + "/" + str(len(filenames.keys())))
        edf = EdfFile(filenames[fName], wantedElectrodes, classes)
        if len(edf.timeSamples):
            edfFiles.append(edf)
        if index == 5: break
    return edfFiles


def get_segments_from_edf(edfFile, minLength=500):
    """
    this function divides a recording into its labeld segments
    :param edfFile: an edfFile object
    :return: a list of objects Segment
    """

    segments = []
    sampFreq = edfFile.samplingFreq
    electrodes = edfFile.electrodeNames
    for l in edfFile.labelInfoList:
        if l[2] in config_classes:
            startTime = float(l[0])
            endTime = float(l[1])
            startIndex = int(startTime * sampFreq)
            endIndex = int(endTime * sampFreq)
            #label = int(l[2])
            label = l[2]
            duration = round(endTime - startTime , 4)
            nSamples = duration * sampFreq
            samples = edfFile.timeSamples[:, startIndex:endIndex]
            if nSamples > minLength:
                s = Segment(sampFreq, nSamples, duration, samples, electrodes, label)
                segments.append(s)


    return segments



def get_all_segments(edfFiles):

    """
    This function iterate over all edfFiles and calls another function
    which gets the segments from the edfFuke object
    :param edfFiles: the list of edfFile objects
    :return: all segments as Segment objects in a list
    """

    segments = []
    for edf in edfFiles:
        print("getting the labeled segments from the recording ", str(edf.filename))
        segments.extend(get_segments_from_edf(edf))
        #if edfFiles.index(edf) == 100: break
    return segments


def clean_segments(listOfSegments):

    cleanedSegments = []
    preprocessor = Preprocessor(config_startShift,
                           config_endShift,
                           config_powerLineFreq,
                           config_bandLowCut,
                           config_bandHighCut)
    for s in listOfSegments:
        cleanedSegments.append(preprocessor.clean(s))

    return cleanedSegments













