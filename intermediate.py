#Author Manuel Pariente 24/07/2019
import torch
import os
from torch.utils import data
import glob
import numpy as np
import soundfile as sf
from librosa import stft

from config import ref_dir, val_ref_dir, hyp_dir, val_hyp_dir

FS = 16000
_REF_LEN = 1.
_HYP_LEN = 1.
REF_LEN = 16320
HYP_LEN = REF_LEN
LOSS_MOMENTS = [600, 150] # Mean, std
L_MIN = 100
L_MAX = 2000
N_FFT = 512
HOP = N_FFT // 4

class SampleLossDataset(data.Dataset):
    def __init__(self, ref_dir=ref_dir, hyp_dir=hyp_dir, ref_len=REF_LEN,
            hyp_len=HYP_LEN, loss_moments=LOSS_MOMENTS, output='abs'):
        self.ref_dir = ref_dir
        self.ref_len = ref_len
        self.hyp_dir = hyp_dir
        self.hyp_len = hyp_len
        self.loss_moments = loss_moments
        self.output = output #in ['abs', 'cat']

        self.ref_files = glob.glob(os.path.join(ref_dir, '**/*.flac'), recursive=True)

    def __len__(self):
        return len(self.ref_files)

    def __getitem__(self, idx):
        file_path = self.ref_files[idx]
        label = np.random.choice((0, 1))
        ref, hyp = self.get_ex(file_path, label)
        # Default center=True : D[:, t] is centered at y[t * hop_length]
        # Good for the aligned strong labels.
        ref_stft = stft(ref, n_fft=N_FFT, win_length=N_FFT, hop_length=HOP)[:-1].T
        hyp_stft = stft(hyp, n_fft=N_FFT, win_length=N_FFT, hop_length=HOP)[:-1].T

        if self.output == 'abs':
            return np.abs(ref_stft), np.abs(hyp_stft), label
        else:
            return ref_stft, hyp_stft, label

    def get_ex(self, ref_path, is_loss):
        hyp_path = ref_path.replace(self.ref_dir, self.hyp_dir)
        max_len = min(len(sf.SoundFile(ref_path)), len(sf.SoundFile(hyp_path)))
        ref_file_len = len(sf.SoundFile(ref_path))
        accept_segment = False
        count = 0
        while not accept_segment:
            count += 1
            ref_start = np.random.randint(0, max_len - self.ref_len - L_MAX)
            ref = sf.read(ref_path, start=ref_start, stop=ref_start + self.ref_len)[0]
            accept_segment = True if np.max(ref) > 0.1 else False
            if count == 5:
                accept_segment=True

        hyp_start = np.random.randint(ref_start, ref_start + self.ref_len -
                self.hyp_len)
        loss_size = 0
        while L_MAX < loss_size < L_MIN and is_loss:
            loss_size = np.random.normal(*self.loss_moments) if is_loss else 0
        hyp = sf.read(hyp_path, start=hyp_start, stop=hyp_start +
                self.hyp_len + loss_size)[0]
        if is_loss:
            loss_start = np.random.randint(L_MIN, self.hyp_len - L_MIN)
            hyp = np.delete(hyp, list(range(loss_start, loss_start + loss_size)))
        return ref, hyp



