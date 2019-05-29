import os

from io_utils import *
from config import *
from data_structures import *
from feature_extraction import *






def main(args):

    print("hi, I am an eeg feature extractor.")
    print("Starting with edf files...")
    edfFiles = get_all_edf_files(args["filenames"], config_electrodes, config_classes)
    segments = get_all_segments(edfFiles)
    cleanedSegments = clean_segments(segments)

    fftExtractors  = sorted([feat_func for feat_func in dir(feature_frequency) if not feat_func.startswith('_')])
    timeExtractors = sorted([feat_func for feat_func in dir(feature_time) if not feat_func.startswith('_')])

    featureExtractor = FeatureExtractor(500,
                                        0.5,
                                        fftExtractors,
                                        timeExtractors,
                                        config_electrodes,
                                        config_bands)
    featureExtractor.extract_features_from_segments(cleanedSegments)
    featureExtractor.write_features_to_csv("dataset")












if __name__ == '__main__':

    args = {}
    labelDict = dict(zip(config_classes, [[] for _ in range(len((config_classes)))]))
    filenames = {}

    for subdir, dirs, files in os.walk(config_rootdir[config_datasetPart]):
        for file in files:
            p = os.path.join(config_rootdir[1], subdir, file)
            if p.endswith("edf"):
                filenames[p[56:-4]] = p.split(".edf")[0]



    args["labels"]      = labelDict
    args["filenames"]   = filenames
    main(args)
