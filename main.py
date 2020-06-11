import os

from io_utils import *
from config import *
from data_structures import *
from feature_extraction import *






def main(args):
    print("hi, I am an eeg feature extractor.")
    print("Starting with edf files...")
    name = "_".join([config_rootdir[args["index"]].split("edf")[0][-7:-1],
                    "B"+str(config_bands[-1]),
                    "O"+str(config_overlap),
                     "W"+str(config_windowSizeSec)])


    edfFiles = get_all_edf_files(args["filenames"], config_electrodes, config_classes)
    segments = get_all_segments(edfFiles)

    fftExtractors  = sorted([feat_func for feat_func in dir(feature_frequency) if not feat_func.startswith('_')])
    timeExtractors = sorted([feat_func for feat_func in dir(feature_time) if not feat_func.startswith('_')])

    featureExtractor = FeatureExtractor(config_windowSizeSec,
                                        config_windowSizeSec*config_samplFreq,
                                        config_overlap,
                                        fftExtractors,
                                        timeExtractors,
                                        config_electrodes,
                                        config_bands)
    featureExtractor.extract_features_from_segments(segments)
    name = "_".join([config_rootdir[args["index"]].split("edf")[0][-7:-1],
                    "B"+str(config_bands[-1]),
                    "O"+str(config_overlap),
                     "W"+str(config_windowSizeSec)])
    featureExtractor.write_features_to_csv(name)



if __name__ == '__main__':

    args = {}
    labelDict = dict(zip(config_classes, [[] for _ in range(len((config_classes)))]))
    filenames = {}
    for i in list(range(3,9)):
        for subdir, dirs, files in os.walk(config_rootdir[i]):
            for file in files:
                p = os.path.join(config_rootdir[i], subdir, file)
                if p.endswith("edf"):
                    filenames[p[56:-4]] = p.split(".edf")[0]
        args["labels"] = labelDict
        args["filenames"] = filenames
        args["index"] = i
        main(args)






