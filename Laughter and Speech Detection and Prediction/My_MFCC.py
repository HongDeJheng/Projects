# -*- coding: utf-8 -*-
"""
Created on Sat Oct 27 12:21:09 2018

@author: Winston & Jim
"""

import numpy as np
from numpy import linalg
from scipy import signal
from scipy import fftpack
from scipy.io import wavfile
import librosa
import math

def get_filter_banks(filters_num,NFFT,samplerate,low_freq=0,high_freq=None):
    ''' Mel Bank
    filers_num: filter numbers
    NFFT:points of your FFT
    samplerate:sample rate
    low_freq: the lowest frequency that mel frequency include
    high_freq:the Highest frequency that mel frequency include
    '''
    #turn the hz scale into mel scale
    low_mel = 2595 * np.log10(1 + low_freq/700)
    high_mel = 2595 * np.log10(1 + high_freq/700)
    #in the mel scale, you should put the position of your filter number 
    mel_points = np.linspace(low_mel, high_mel, filters_num + 2)
    #get back the hzscale of your filter position
    hz_points = ((10 ** (mel_points/2595)) - 1) * 700
    #Mel triangle bank design
    binn = np.floor((NFFT + 1) * hz_points / samplerate)
    print(binn)
    fbank = np.zeros([filters_num, int(NFFT/2+1)])
    ###################
    #Your code
    for m in range(1, filters_num + 1):
        f_minus = int(binn[m-1])
        f = int(binn[m])
        f_plus = int(binn[m+1])
        
        for k in range(f_minus, f):
            fbank[m-1, k] = (k - binn[m-1]) / (binn[m] - binn[m-1])
        for k in range(f, f_plus + 1):
            fbank[m-1, k] = (binn[m+1] - k) / (binn[m+1] - binn[m])
    ##################
    return fbank
    
def My_MFCC_function(x, s):
    '''
    In this block, please revise your MFCC function from lab 2. Let your MFCC.py be
    a function or a class type with I/O.
    Input:
        x: Audio signal array 
        s: Sampling rate
    Output:
        mfcc with dimension of n_frames * n_coefficients
    '''
    '''
    Your MFCC operation codes here
    '''
    ### parameters define
    fs = s                                # SampleRate
    signal_length = len(x)                # Signal length
    win_length = 0.025                    # Window_size(sec)
    win_step = 0.01                       # Window_hop(sec)
    frame_length = int(win_length * fs)   # Frame length(samples)
    frame_step = int(win_step * fs)       # Step length(samples)
    emphasis_coeff = 0.97                 # pre-emphasis para
    filters_num = 26                      # Filter number
    NFFT = 512
    low_freq = 0
    high_freq = int(fs/2)
    
    ### pre-emphasis
    signal = np.append(x[0], x[1:] - emphasis_coeff * x[:-1])
    
    ### calculate frame number
    frames_num = 1 + int(math.ceil((1.0 * signal_length - frame_length) / frame_step))
    
    #padding    
    pad_length = int((frames_num - 1) * frame_step + frame_length)  
    zeros = np.zeros((pad_length - signal_length,))          
    pad_signal = np.concatenate((signal, zeros))  
    
    #split into frames
    indices = np.tile(np.arange(0, frame_length), (frames_num, 1)) + np.tile(np.arange(0, frames_num * frame_step, frame_step), (frame_length, 1)).T  
    indices = np.array(indices, dtype=np.int32) 
    frames = pad_signal[indices] 
    frames *= np.hamming(frame_length)
    
    mag_frames = np.abs(np.fft.rfft(frames, NFFT))
    pow_frames = ((1.0 / NFFT) * (mag_frames ** 2))
    
    fb = get_filter_banks(filters_num, NFFT, fs, low_freq, high_freq) 
    
    #plt.figure(1)
    #plt.title("Traingle Band-pass Filter %d" % filters_num)
    #for i in range(len(fb)):
    #    plt.plot(fb[i])
    #plt.show()
    #plt.savefig("result/Traingle Band-pass Filter 10.png", dpi=300, bbox_inches='tight')

    feat = np.dot(pow_frames, fb.T)
    feat = np.where(feat == 0, np.finfo(float).eps, feat)
    feat = 20 * np.log10(feat)
    
    mfcc = fftpack.dct(feat, norm = 'ortho')[:, :filters_num]
    #mfcc_2to13 = dct(feat, type = 2, axis = 1, norm = 'ortho')[:, 1:13]
    
    #plt.figure(2)
    #plt.title("MFCC_%d" % filters_num)
    #for i in range(filters_num):
    #    plt.plot(mfcc[i, :])
    #plt.show()
    #plt.savefig("result/MFCC_10.png", dpi=300, bbox_inches='tight')
    
    return mfcc

def Cal_feat(path):
    '''
    This function calls My_MFCC_function(x, s) to calculate the mfcc given the path
    In this lab, we downsample the original audio files to 16k Hz.
    Input:
        The path of audio files
    Output:
        The same as the output of My_MFCC_function(x, s)
    '''
    x, s = librosa.load(path, sr=None)
    x = librosa.resample(x, s, 16000)
    s = 16000
    x = x / max(x)
    return My_MFCC_function(x, s)