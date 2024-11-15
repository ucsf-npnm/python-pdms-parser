"""scrap data from programming reports (individual pdf files)
"""

# Import standard libraries #
import PyPDF2
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import os
import pathlib

from ParserTools2 import GetFilePaths, MergeFiles

# User-specified inputs #
patient_id = 'PR05'
input_dir  = '/userdata/dastudillo/patient_data/pdms' #Keep input pdf files in a separate folder
output_dir   = '/userdata/dastudillo/patient_data'

files = GetFilePaths(input_dir)

# Main code #
col_labs = ['programming_pst_timestamp', 'stim_status', 'pos_contact', 'neg_contact', 'amplitude', 'frequency', 'pulsewidth', 'duration']
final_df = pd.DataFrame(data=None, index=None, columns=None)

for i in files:
    with open(i, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    split_text = text.split('\n')
    
    #Retrieve programming timestamp
    for line in split_text:  
        if '(US/Pacific) Programming' in line:
            programming_timestamp_raw = line.split(') ')[1].split(' (')[0]
    programming_timestamp = datetime.strptime(programming_timestamp_raw, '%b %d, %Y %H:%M:%S')

    #Retrieve stim status
    if 'Responsive Therapies Behavior for Therapy 1' in text:
        stim_status = 'ON'
    if 'Responsive Therapies Behavior for Therapy 1' not in text:
        stim_status = 'OFF'

    #Retrieve stim settings
    if stim_status=='ON':
        for line in split_text:
            if ('Current' in line) & ('mA' in line):
                amplitude = float(line.split(' ')[1])
                stim_grid = split_text[split_text.index(line)-9: split_text.index(line)]
            if ('Frequency' in line) & ('Hz' in line):
                frequency = float(line.split(' ')[1])
            if ('PW Per Phase' in line) & ('µs' in line):
                pw = int(line.split(' ')[3])
            if ('Burst Duration' in line) & ('ms' in line):
                burst_duration = int(line.split(' ')[2])*2

        contacts = [x.split(' ')[0] for x in stim_grid]
        polarity = [x.split(' ')[1] for x in stim_grid]
        pos_contact = []
        neg_contact = []
        for i, j in zip(contacts, polarity):
            if j == '+':
                pos_contact.append(i)
            if j == '-':
                neg_contact.append(i)

    if stim_status=='OFF':
        amplitude = 0.0
        frequency = 0.0
        pw = 0
        burst_duration = 0
        pos_contact = 'None'
        neg_contact = 'None'

    values = [programming_timestamp, stim_status, pos_contact, neg_contact, amplitude, frequency, pw, burst_duration]
    final_df = pd.concat([final_df, pd.Series(values)], axis=1)

final_df = final_df.T
final_df.columns = col_labs

final_df_save = final_df.sort_values(by='programming_pst_timestamp').reset_index(drop=True)

del final_df
del final_df_save

"""End of code"""