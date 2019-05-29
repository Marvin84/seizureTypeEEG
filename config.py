#Paths
config_datasetPart = 2

prePath = "/Users/tinaraissi/workspace/EEG/tuh-eeg-auto-diagnosis/"
#prePath = "/Users/laneskij/workspaces/seizureTypeEEG/"
config_rootdir = {1: prePath+"v1.4.0_1/edf/train/01_tcp_ar/",
                  2: prePath+"v1.4.0_2/edf/train/02_tcp_le/",
                  3: prePath+"v1.4.0_3/edf/train/03_tcp_ar_a/",
                  4: prePath+"dev_2/edf/dev_test/02_tcp_le/",
                  5: prePath+"dev_3/edf/dev_test/03_tcp_ar_a/",}


#Objects
"""
config_electrodes = ['A1', 'A2',
                       'C3', 'C4', 'CZ',
                       'F3', 'F4', 'F7', 'F8', 'FP1','FP2', 'FZ',
                       'O1', 'O2',
                       'P3', 'P4', 'PZ',
                       'T3', 'T4', 'T5', 'T6']
                       
"""

config_electrodes = ['A1', 'A2',
                     'C3', 'C4', 'CZ',
                     'F3', 'F4', 'F7', 'F8', 'FP1','FP2', 'FZ',
                     'O1', 'O2',
                     'P3', 'P4', 'PZ',
                     'T3', 'T4', 'T5', 'T6']

#config_classes = {'bckg': 1 ,'fnsz': 2,'gnsz': 3,'spsz': 4,'cpsz': 5,'absz':6,'tnsz': 7,'tcsz': 8,'mysz': 9}
config_classes = ['fnsz','gnsz','spsz','cpsz','absz','tnsz','tcsz','mysz']


#for the notch filter and other functions
config_windows = [
    'barthann',
    'bartlett',
    'blackman',
    'blackmanharris',
    'bohman',
    'boxcar',
    'cosine',
    'flattop',
    'hamming',
    'hann',
    'nuttall',
    'parzen',
    'triang'
]


#data cleanning
#config_bands         = [1, 4, 8, 12, 18, 24, 30, 60, 90]
config_bands         = [1, 4, 8, 12, 18, 24]
config_timeThreshold = 100
config_startShift    = 0.05
config_endShift      = 0.05
config_powerLineFreq = 60
config_bandLowCut    = 0.2
config_bandHighCut   = 100

#Feature extraction
config_windowSizeSec    = 1
config_samplFreq        = 250
config_overlap          = 0.75