# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 14:15:52 2018

@author: Jim
"""

import csv

with open('./result/predict.csv', 'w', newline='') as csvfile:
    with open('./Laughter_Speech_data/S022/label.csv', 'r', newline='') as tmp:
        rows = csv.reader(tmp)
        for row in rows:
            writer = csv.writer(csvfile)
            writer.writerow(row)
            
    with open('./Laughter_Speech_data/S023/label.csv', 'r', newline='') as tmp:
        rows = csv.reader(tmp)
        for row in rows:
            writer = csv.writer(csvfile)
            writer.writerow(row)
            
    with open('./Laughter_Speech_data/S024/label.csv', 'r', newline='') as tmp:
        rows = csv.reader(tmp)
        for row in rows:
            writer = csv.writer(csvfile)
            writer.writerow(row)
    
    with open('./Laughter_Speech_data/S025/label.csv', 'r', newline='') as tmp:
        rows = csv.reader(tmp)
        for row in rows:
            writer = csv.writer(csvfile)
            writer.writerow(row)
            
with open('./result/kaggle.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Id', 'Answer'])
    for idx in range(0,205):
       writer.writerow([idx])