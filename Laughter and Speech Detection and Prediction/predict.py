# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 01:52:20 2018

@author: user
"""

import My_MFCC # Remember to revise original mfcc.py.
import os
import numpy as np
import csv
from shutil import copy
from sklearn import preprocessing
import joblib

'''
In predict.py, please load the best model you have trained from train.py.
Please read the first three column of result.csv and process the testing data to predict if the 
segment is "laughter" or "speech" and write your predict results in the fourth column of result.csv.
'''
    
def frame_to_second(frame):
    '''
    This function helps you to transfer from frames to seconds
    
    Remember to fill in your hop size
    '''
    sr = 16000
    hop = 0.01
    hop_size = sr * hop
    sample = (np.asanyarray(frame) * hop_size).astype(int)
    time = sample / float(sr)
    return time

def second_to_frame(start_time, end_time, sr, hop_length):
    '''
    This function helps you to transfer from seconds to frames
    '''
    start_samples = (np.asanyarray(start_time) * sr).astype(int)
    end_samples = (np.asanyarray(end_time) * sr).astype(int)

    start_samples = np.asanyarray(start_samples)
    end_samples = np.asanyarray(end_samples)
    
    start_frame = np.floor((start_samples) // hop_length).astype(int)
    end_frame = np.floor((end_samples) // hop_length).astype(int)
    return start_frame, end_frame

if __name__ == '__main__':
    
    