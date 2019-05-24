import os

from io_utils import *


from config import *
from feature_extraction import *






def main(args):

    print("hi, I am an eeg feature extractor.")
    print("Starting with edf files...")
    edfFiles = get_all_edf_files(args["filenames"], config_electrodes, config_classes)
    segments = get_all_segments(edfFiles)
    features = {}
    for s in segments:
        featureExtractor = FeatureExtractor(500,
                                            0.5,
                                            s.fftExtractors,
                                            s.timeExtractors,
                                            s.electrodeNames,
                                            config_bands)
        featureExtractor.extract_features_in_freq(s)
        featureExtractor.extract_features_in_time(s)








if __name__ == '__main__':

    args = {}
    labelDict = dict(zip(list(config_classes.values()), [[] for _ in range(len((config_classes.keys())))]))
    filenames = {}

    for subdir, dirs, files in os.walk(config_rootdir[config_datasetPart]):
        for file in files:
            p = os.path.join(config_rootdir[1], subdir, file)
            if p.endswith("edf"):
                filenames[p[56:-4]] = p.split(".edf")[0]



    args["labels"]      = labelDict
    args["filenames"]   = filenames
    main(args)
