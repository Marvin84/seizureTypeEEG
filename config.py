#Paths
config_datasetPart = 4


#prePath = "/Users/tinaraissi/workspace/EEG/tuh-eeg-auto-diagnosis/"
#prePath = "/Users/laneskij/workspaces/seizureTypeEEG/"
prePath = "/Volumes/Laneskij/"
config_rootdir = {1: prePath+"train_0/edf/train/01_tcp_ar/",
                  2: prePath+"train_01/edf/train/02_tcp_le/",
                  3: prePath+"train_2/edf/train/03_tcp_ar_a/",
                  4: prePath+"test_00/edf/dev_test/01_tcp_ar/",
                  5: prePath+"test_01/edf/dev_test/02_tcp_le/",
                  6: prePath+"test_02/edf/dev_test/03_tcp_ar_a/"}


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
config_bands         = [1, 4, 8, 12, 18, 24, 30, 60, 90]

config_timeThreshold = 100
config_startShift    = 0.05
config_endShift      = 0.05
config_powerLineFreq = 60
config_bandLowCut    = 0.2
config_bandHighCut   = 100

#Feature extraction
config_windowSizeSec    = 1
config_samplFreq        = 250
config_overlap          = 0.5