# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 15:35:41 2018

@author: HongDe
"""

from sklearn.svm import SVC
from sklearn.metrics import recall_score
from sklearn import preprocessing
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import joblib
import os
import time
import csv
import operator
from preprocess import second_to_frame

def load_training_data(path):
    ### empty numpy array for storing train data
    X_train = np.empty((0, 104))
    y_train = np.empty((0, 1))
    Test = ['S022','S023','S024','S025']
    for subdir in sorted(os.listdir(path)):
        if subdir not in Test: 
            for subject in os.listdir(path + '/' + subdir):
                ### load X_train
                if subject != 'label.csv' and subject != 'label_sorted.csv':
                    #print(subject)
                    tmp = np.load(path + '/' + subdir + '/' + subject)
                    tmp_std = np.std(tmp, axis = 0)     ### standardization of the column
                    tmp_max = np.max(tmp, axis = 0)     ### max of the column
                    tmp_min = np.min(tmp, axis = 0)     ### min of the column
                    tmp_mean = np.mean(tmp, axis = 0)   ### mean of the column
                    ### every feature above is (1, 26), and we want one row to represent one audio data
                    ### so we use np.hstack to let it become (1, 104)
                    total = np.hstack((np.hstack((np.hstack((tmp_std, tmp_max)), tmp_min)), tmp_mean))
                    ### one row represents one audio data, np.vstack extend the data we load
                    ### when we load new data, it will be stacked to new row
                    X_train = np.vstack((X_train, np.reshape(total, (1, 104))))
                ### load y_train
                elif subject == 'label_sorted.csv':
                    df = pd.read_csv((path + '/' + subdir + '/' + subject), header = None) 
                    encode = {'speech' : 0, 'laughter' : 1}
                    tmp_y = df[3].replace(encode)
                    tmp_y = np.reshape(np.array(tmp_y), (tmp_y.shape[0], 1))
                    y_train = np.vstack((y_train, tmp_y))
    ### change shape (X, 1) to shape (X, ) to avoid warning                
    y_train = np.reshape(y_train, (y_train.shape[0], ))
    ### store X_train and y_train in pkl
    joblib.dump(X_train, os.path.join('./training_set', 'X_train_2.pkl'))
    joblib.dump(y_train, os.path.join('./training_set', 'y_train_2.pkl'))
       
    return X_train, y_train


def load_testing_data(path):
    X_test = np.empty((0, 104))
    Test = ['S022','S023','S024','S025']
    for subdir in os.listdir(path):
        if subdir in Test: 
            with open((path + '/' + subdir + '/label.csv'), newline='') as csvfile:
                rows = csv.reader(csvfile)
                for row in rows:
                    start, end = second_to_frame(float(row[1]), float(row[2]), 16000, 160)
                    ### when loading test data, we can't sort it first because we can't sort the result's order
                    ### so we need to see what we need to load according to predict.csv
                    tmp = np.load(path + '/' + subdir + '/' + row[0] + ' ' + str(start) + '_' + str(end) + '.npy')
                    tmp_std = np.std(tmp, axis = 0)     ### standardization of the column
                    tmp_max = np.max(tmp, axis = 0)     ### max of the column
                    tmp_min = np.min(tmp, axis = 0)     ### min of the column
                    tmp_mean = np.mean(tmp, axis = 0)   ### mean of the column
                    ### every feature above is (1, 26), and we want one row to represent one audio data
                    ### so we use np.hstack to let it become (1, 104)
                    total = np.hstack((np.hstack((np.hstack((tmp_std, tmp_max)), tmp_min)), tmp_mean))
                    X_test = np.vstack((X_test, np.reshape(total, (1, 104))))
    
    joblib.dump(X_test, os.path.join('./testing_set', 'X_test_2.pkl'))
                      
    return X_test
            

'''
Do cross validation here
'''
### I'll do cross validation with train together

'''
Do training here
'''
def Train(penalty, X_train, y_train, X_test):
    ### standarized the data
    sc = StandardScaler()
    sc.fit(X_train)
    X_train_std = sc.transform(X_train)
    X_test_std = sc.transform(X_test)
    
    ### define classifier
    svm = SVC()
    
    ### classifier's parameters
    param = [{
        'C' : penalty,
        'kernel' : ['rbf']
    }]
    
    ### GridSearchCV with RBF SVM and 5 fold cross validation
    gs_svm = GridSearchCV(estimator = svm, param_grid = param, cv = 5, scoring = 'accuracy')
    gs_svm.fit(X_train_std, y_train)
    print("Best accuracy : %f" % gs_svm.best_score_)
    print("Best accuracy's parameters :", gs_svm.best_params_)
    ### store the best model
    joblib.dump(gs_svm.best_estimator_, os.path.join('./result', 'best_model_2.pkl'))
    
    return gs_svm.best_estimator_, X_train_std, X_test_std


def Sort():   
    for subdir in os.listdir(path):
        for subject in os.listdir(path + '/' + subdir):
            if subject == 'label.csv':
                data = csv.reader(open(path + '/' + subdir + '/' + subject))
                ### sort label.csv by first column's alphabetical order and save it into label_sorted.csv
                sortedlist = sorted(data, key = operator.itemgetter(0))
                with open((path + '/' + subdir + '/label_sorted.csv'), 'w', newline='') as f:
                    rows = csv.writer(f)
                    for row in sortedlist:
                        rows.writerow(row)
                        
    
if __name__ == '__main__':

    path = './MFCC_seg_feat'
    
    '''
    Define your training parameters here
    '''
    ### define penalty for GridSearch
    C = np.around(np.linspace(0.1, 10.0, num=100), decimals = 2)
    #print(C)
    
    tic = time.time()
    ### Sorting function, to sort the loading order of npy file and create an correspond label csv file
    Sort()
    ### load data
    X_train, y_train = load_training_data(path)
    X_test = load_testing_data(path)
    
    ### check the size of data
    print(X_train.shape)
    print(y_train.shape)
    print(X_test.shape)
    
    df = pd.read_csv("../result.csv", header = None)
    test_target = df[3]
    encode = {'speech' : 0, 'laughter' : 1}
    y_test = test_target.replace(encode)
    y_test = np.reshape(np.array(y_test), (y_test.shape[0], ))
    print(y_test.shape)
    joblib.dump(y_test, os.path.join('./testing_set', 'y_test.pkl'))

    toc = time.time()
    
    print("Takes ", toc - tic, "seconds.")
    
    tic = time.time()
    ### Get the best model and the standarized data
    clf, X_train_std, X_test_std = Train(C, X_train, y_train, X_test)
    toc = time.time()
    print("SVM takes ", toc - tic, "seconds.")
    
    ### predict
    clf.fit(X_train_std, y_train) 
    y_pred = clf.predict(X_test_std)
    y_pred_decode = []
    for ele in y_pred:
        if(ele == 0):
            y_pred_decode.append('speech')
        else:
            y_pred_decode.append('laughter')
    #print(y_pred_decode)
    
    ### write the predict result into a csv file
    with open('./result/kaggle_3.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Id', 'Answer'])
        for idx in range(0,205):
            writer.writerow([idx, y_pred_decode[idx]])
    
    
    num_correct = (y_pred == y_test).sum()
    accuracy = float(num_correct) / y_test.shape[0]
    print("Accuracy = ",accuracy)
    