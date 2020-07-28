# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 14:29:23 2018

@author: Jim
"""

import My_MFCC # Remember to revise original mfcc.py.
import os
import numpy as np
import csv
from shutil import copy
import joblib

# path of dataset
DATASET_PATH = './Laughter_Speech_data'


def second_to_frame(start_time, end_time, sr, hop_length):
    '''
    This function need to transfer the unit from seconds to frame
    Input:
        start_time: start time in seconds
        end_time: end time in seconds
        sr: sampling rate, which is 16k in this project
        hop_length: hop size of the frames which equals the setting in your MFCC. Unit is samples.
    Output:
        Unit is frame
    '''
    start_samples = (np.asanyarray(start_time) * sr).astype(int)
    end_samples = (np.asanyarray(end_time) * sr).astype(int)

    start_samples = np.asanyarray(start_samples)
    end_samples = np.asanyarray(end_samples)
    
    start_frame = np.floor((start_samples) // hop_length).astype(int)
    end_frame = np.floor((end_samples) // hop_length).astype(int)
    
    return start_frame, end_frame
    
def Cal_MFCC():
    '''
    Calculate the MFCCs of the whole integrated audio files and store these features into "MFCC_feat" directory
    Each of the MFCCs files is named by the filename of the original audio files.
    '''
    # path of MFCC_feat directory
    DIR_PATH = './MFCC_feat'
    
    if not os.path.isdir(DIR_PATH):
        os.mkdir(DIR_PATH)
    '''
    Scan the raw data in "Laughter_Speech_data" directory and throw the raw data into your MFCC function
    '''
    for subject in os.listdir(DATASET_PATH):
        SUBJECT_FILE_PATH = os.path.join(DATASET_PATH, subject)
        for file in os.listdir(SUBJECT_FILE_PATH):
            if file.split('.')[-1] == 'wav':
                WAV_PATH = os.path.join(SUBJECT_FILE_PATH, file)
                '''
                Input of "Cal_feat" function is the file path and return mfcc 
                with dimension of "n_frames * n_coefficients"
                '''
                mfcc = My_MFCC.Cal_feat(WAV_PATH)
                FILE_PATH = os.path.join(DIR_PATH, file.split('.')[0])
                np.save(FILE_PATH, mfcc)

def Segment_MFCC(hop_size, sr):
    '''
    Because there are only some segmentations with laughter or speech in original audio files,
    we need to cut the MFCCs into wanted segmentations with only laughter or only speech.
    The start and end points when laughter/speech occurs are described in the "label.csv" in each subject file.
    4 columns in "label.csv" are "audio filename", "start time(secs)", "end time(secs)" and "label".
    "label" is either "laughter" or "speech"
    '''
    DIR_PATH = './MFCC_seg_feat'
    MFCC_PATH = './MFCC_feat'
    
    if not os.path.isdir(DIR_PATH):
        os.mkdir(DIR_PATH)
        
    for subject in os.listdir(DATASET_PATH):
        SUBJECT_FILE_PATH = os.path.join(DATASET_PATH, subject)
        for file in os.listdir(SUBJECT_FILE_PATH):
            if file.split('.')[-1] == 'csv':
                CSV_PATH = os.path.join(SUBJECT_FILE_PATH, file)
                '''
                Copy "label.csv" to each subject directory in "MFCC_seg_feat"
                '''
                if not os.path.isdir(os.path.join(DIR_PATH, subject)):
                        os.mkdir(os.path.join(DIR_PATH, subject))
                copy(CSV_PATH, os.path.join(DIR_PATH, subject))
                '''
                Read "label.csv" in each subject's directory
                '''
                with open(CSV_PATH, newline='') as csvfile:
                    rows = csv.reader(csvfile)
                    for row in rows:
                        PATH = os.path.join(MFCC_PATH, row[0] + '_mic.npy')
                        start, end = second_to_frame(float(row[1]), float(row[2]), sr, hop_size*sr)
                        mfcc = np.load(PATH)
                        np.save(os.path.join(DIR_PATH, subject, row[0]+' '+str(start)+'_'+str(end)),mfcc[start:end,:])


def Per_frame_label(hop_size, sr):
    '''
    Because the labeling rule described in "label.csv" is "per second labeling".
    This function changes this labeling rule into "per frame labeling"
    '''
    DIR_PATH = './MFCC_seg_feat'
    PKL_PATH = './PKL'
    Test = ['S022','S023','S024','S025']
    
    for subject in os.listdir(DIR_PATH):
        SUBJECT_FILE_PATH = os.path.join(DIR_PATH, subject)
        CSV_PATH = os.path.join(SUBJECT_FILE_PATH, 'label.csv')
        raw_data = []
        label = []
        with open(CSV_PATH, newline='') as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                for file in os.listdir(SUBJECT_FILE_PATH):
                    if row[0] == file.split(' ')[0]:
                        start, end = second_to_frame(float(row[1]), float(row[2]), sr, hop_size*sr)
                        if str(start)==file.split(' ')[1].split('_')[0] and str(end)==file.split(' ')[1].split('_')[-1].split('.')[0]:
                            seg_mfcc = np.load(os.path.join(SUBJECT_FILE_PATH,file))
                            n_bins = seg_mfcc.shape[0]
                            for idx in range(n_bins):
                                raw_data.append(list(seg_mfcc[idx,:]))
                                if subject not in Test:
                                    if row[3]=='laughter':
                                        label.append(1)
                                    elif row[3]=='speech':
                                        label.append(0)
        if not os.path.isdir(PKL_PATH):
            os.mkdir(PKL_PATH)
            
        joblib.dump([raw_data, label], os.path.join(PKL_PATH, subject+'.pkl'))


if __name__ == '__main__':
    '''
    Please fill in your hop size the same as the hop size in your MFCC setting.
    (the unit is second)
    '''
    hop_size = 0.01

    Cal_MFCC()
    Segment_MFCC(hop_size, 16000)
    Per_frame_label(hop_size, 16000)