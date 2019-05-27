import numpy as np
import pandas as pd


from functions import feature_frequency
from functions import feature_time





def get_feature_vector_from_segment(featureExtractor, segment):

    features = {}
    fftFeat  = featureExtractor.extract_features_in_freq(segment)
    timeFeat = featureExtractor.extract_features_in_time(segment)
    features.update(fftFeat)
    features.update(timeFeat)

    return features
