import os

from io_utils import *
from data_structures import *
from preprocessing import *
from config import *




def main():
    print("hi, I am an eeg feature extractor.")





if __name__ == '__main__':

    segLabelFilenames = {}

    for subdir, dirs, files in os.walk(config_rootdir[config_datasetPart]):
        for file in files:
            p = os.path.join(subdir, file)
            if p.endswith("edf"):
                segLabelFilenames[p[56:-4]] = p.split(".edf")[0]


    main()
