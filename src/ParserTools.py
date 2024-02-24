## Custom function to scrap pdf files downloaded from PDMS ##

#Import standard libraries
import pandas as pd
import numpy as np
import os
import pathlib
import pdfminer
from pdfminer.high_level import extract_text
from PyPDF2 import PdfFileMerger
from datetime import datetime
import pathlib

#Get list of files specifying folder path and file format as string
def GetFilePaths(FileDirectory, FileFormat):
    FileNames = sorted(filter(lambda x: True if FileFormat in x else False, os.listdir(FileDirectory)))
    FilePaths = []
    for i in range(len(FileNames)):
        FilePaths.append(FileDirectory+FileNames[i])
    return FilePaths

#Merge pdf files
def MergeFiles(FileDirectory, ListOfFiles, NewFileName):
    #create and instance of PdfFileMerger() class
    merger = PdfFileMerger()
    #iterate over the list of file paths
    for file in ListOfFiles:
        #Append PDF files
        merger.append(file)
    #write out the merged PDF
    outpath = pathlib.Path(FileDirectory, NewFileName)
    merger.write(outpath)
    merger.close()
    return outpath

#Parser code
def RunParser(FilePath):
    #Extract all text from pdf 
    text = extract_text(FilePath)
    #Create list with strings
    lines = text.split('\n')

    #Select timestamp, duration and type of event 
    EventTimestamp = [a for a in lines if ('Mon,' in a or 'Tue,' in a or 'Wed,' in a \
                                           or 'Thu,' in a or 'Fri,' in a or 'Sat,' in a or 'Sun,' in a)]
    EventDuration = [b for b in lines if ('seconds' in b or 'second' in b)]
    EventType = [c for c in lines if ('Pattern A2' in c \
                                   or 'Pattern A1' in c \
                                   or 'Pattern B1' in c \
                                   or 'Pattern B2' in c \
                                   or 'Pattern A1A2' in c \
                                   or 'Pattern B1B2' in c \
                                   or 'Magnet applied' in c)]

    #Create list of lists that will be use as input data for final dataframe columns
    DataForDf = []
    for i in range(len(EventTimestamp)):
        DataForDf.append([EventTimestamp[i], EventDuration[i], EventType[i]])

    #Create initial dataframe
    InitDataFrame = pd.DataFrame(DataForDf, columns = ['EventTimestamp', 'EventDuration', 'EventType'])
    #get rid of string so duration is numerical data
    InitDataFrame['EventDuration'] = InitDataFrame['EventDuration'].str.replace('seconds','')

    #Convert timestamps to datetime object
    EventTimestampsList = list(InitDataFrame['EventTimestamp'])
    EventDateTimeList =  []
    for i in range(len(EventTimestampsList)):
        EventDateTimeList.append(datetime.strptime(EventTimestampsList[i], '%a, %b %d, %Y %H:%M:%S'))

        #Update timestamps in dataframe
    NewDataFrame = InitDataFrame.copy()
    del InitDataFrame
    NewDataFrame['EventTimestamp'] = EventDateTimeList
    NewDataFrame = NewDataFrame.sort_values(by='EventTimestamp').reset_index(drop=True)

    #Assign detections for pattern A1
    conditionsA1 = [
        (NewDataFrame['EventType'].isin([d for d in NewDataFrame['EventType'] if ('Pattern A1 ; 1 Responsive Therapy' in d or 'Pattern A1 ; 1 Responsive Therapy; Insufficient Charge;' in d)])),
        (NewDataFrame['EventType'].isin([e for e in NewDataFrame['EventType'] if ('Pattern A1 ; 2 Responsive Therapies' in e or 'Pattern A1 ; 2 Responsive Therapies; Insufficient Charge;' in e)])),
        (NewDataFrame['EventType'].isin([f for f in NewDataFrame['EventType'] if ('Pattern A1 ; 3 Responsive Therapies' in f or 'Pattern A1 ; 3 Responsive Therapies; Insufficient Charge;' in f)])),
        (NewDataFrame['EventType'].isin([g for g in NewDataFrame['EventType'] if ('Pattern A1 ; 4 Responsive Therapies' in g or 'Pattern A1 ; 4 Responsive Therapies; Insufficient Charge;' in g)])),
        (NewDataFrame['EventType'].isin([j for j in NewDataFrame['EventType'] if ('Pattern A1 ; 5 Responsive Therapies' in j or 'Pattern A1 ; 5 Responsive Therapies; Insufficient Charge;' in j)])),
        (NewDataFrame['EventType'].isin([k for k in NewDataFrame['EventType'] if ('Pattern A1 Therapy Delivery Inhibited by' in k)])), #will consider events inhibited by cap limit or PEI
        (NewDataFrame['EventType'] == 'Magnet applied')]
    #Create a list of the values we want to assign for each condition
    valuesA1 = ['1', '2', '3', '4', '5', '1', '0']

    #Assign detections for pattern A2
    conditionsA2 = [
        (NewDataFrame['EventType'].isin([d for d in NewDataFrame['EventType'] if ('Pattern A2 ; 1 Responsive Therapy' in d or 'Pattern A2 ; 1 Responsive Therapy; Insufficient Charge;' in d)])),
        (NewDataFrame['EventType'].isin([e for e in NewDataFrame['EventType'] if ('Pattern A2 ; 2 Responsive Therapies' in e or 'Pattern A2 ; 2 Responsive Therapies; Insufficient Charge;' in e)])),
        (NewDataFrame['EventType'].isin([f for f in NewDataFrame['EventType'] if ('Pattern A2 ; 3 Responsive Therapies' in f or 'Pattern A2 ; 3 Responsive Therapies; Insufficient Charge;' in f)])),
        (NewDataFrame['EventType'].isin([g for g in NewDataFrame['EventType'] if ('Pattern A2 ; 4 Responsive Therapies' in g or 'Pattern A2 ; 4 Responsive Therapies; Insufficient Charge;' in g)])),
        (NewDataFrame['EventType'].isin([j for j in NewDataFrame['EventType'] if ('Pattern A2 ; 5 Responsive Therapies' in j or 'Pattern A2 ; 5 Responsive Therapies; Insufficient Charge;' in j)])),
        (NewDataFrame['EventType'].isin([k for k in NewDataFrame['EventType'] if ('Pattern A2 Therapy Delivery Inhibited by' in k)])),
        (NewDataFrame['EventType'] == 'Magnet applied')]
    #Create a list of the values we want to assign for each condition
    valuesA2 = ['1', '2', '3', '4', '5', '1', '0']

        #Assign detections for pattern B1
    conditionsB1 = [
        (NewDataFrame['EventType'].isin([d for d in NewDataFrame['EventType'] if ('Pattern B1 ; 1 Responsive Therapy' in d or 'Pattern B1 ; 1 Responsive Therapy; Insufficient Charge;' in d)])),
        (NewDataFrame['EventType'].isin([e for e in NewDataFrame['EventType'] if ('Pattern B1 ; 2 Responsive Therapies' in e or 'Pattern B1 ; 2 Responsive Therapies; Insufficient Charge;' in e)])),
        (NewDataFrame['EventType'].isin([f for f in NewDataFrame['EventType'] if ('Pattern B1 ; 3 Responsive Therapies' in f or 'Pattern B1 ; 3 Responsive Therapies; Insufficient Charge;' in f)])),
        (NewDataFrame['EventType'].isin([g for g in NewDataFrame['EventType'] if ('Pattern B1 ; 4 Responsive Therapies' in g or 'Pattern B1 ; 4 Responsive Therapies; Insufficient Charge;' in g)])),
        (NewDataFrame['EventType'].isin([j for j in NewDataFrame['EventType'] if ('Pattern B1 ; 5 Responsive Therapies' in j or 'Pattern B1 ; 5 Responsive Therapies; Insufficient Charge;' in j)])),
        (NewDataFrame['EventType'].isin([k for k in NewDataFrame['EventType'] if ('Pattern B1 Therapy Delivery Inhibited by' in k)])),
        (NewDataFrame['EventType'] == 'Magnet applied')]
    #Create a list of the values we want to assign for each condition
    valuesB1 = ['1', '2', '3', '4', '5', '1', '0']

    #Assign detections for pattern B2
    conditionsB2 = [
        (NewDataFrame['EventType'].isin([d for d in NewDataFrame['EventType'] if ('Pattern B2 ; 1 Responsive Therapy' in d or 'Pattern B2 ; 1 Responsive Therapy; Insufficient Charge;' in d)])),
        (NewDataFrame['EventType'].isin([e for e in NewDataFrame['EventType'] if ('Pattern B2 ; 2 Responsive Therapies' in e or 'Pattern B2 ; 2 Responsive Therapies; Insufficient Charge;' in e)])),
        (NewDataFrame['EventType'].isin([f for f in NewDataFrame['EventType'] if ('Pattern B2 ; 3 Responsive Therapies' in f or 'Pattern B2 ; 3 Responsive Therapies; Insufficient Charge;' in f)])),
        (NewDataFrame['EventType'].isin([g for g in NewDataFrame['EventType'] if ('Pattern B2 ; 4 Responsive Therapies' in g or 'Pattern B2 ; 4 Responsive Therapies; Insufficient Charge;' in g)])),
        (NewDataFrame['EventType'].isin([j for j in NewDataFrame['EventType'] if ('Pattern B2 ; 5 Responsive Therapies' in j or 'Pattern B2 ; 5 Responsive Therapies; Insufficient Charge;' in j)])),
        (NewDataFrame['EventType'].isin([k for k in NewDataFrame['EventType'] if ('Pattern B2 Therapy Delivery Inhibited by' in k)])),
        (NewDataFrame['EventType'] == 'Magnet applied')]
    #Create a list of the values we want to assign for each condition
    valuesB2 = ['1', '2', '3', '4', '5', '1', '0']

        #Assign therapies count
    conditionsT = [
        (NewDataFrame['EventType'].isin([x for x in NewDataFrame['EventType'] if ('Pattern A1 ; 1 Responsive Therapy' in x or 'Pattern A1 ; 1 Responsive Therapy; Insufficient Charge;' in x)])),
        (NewDataFrame['EventType'].isin([x for x in NewDataFrame['EventType'] if ('Pattern A1 ; 2 Responsive Therapies' in x or 'Pattern A1 ; 2 Responsive Therapies; Insufficient Charge;' in x)])),
        (NewDataFrame['EventType'].isin([f for f in NewDataFrame['EventType'] if ('Pattern A1 ; 3 Responsive Therapies' in f or 'Pattern A1 ; 3 Responsive Therapies; Insufficient Charge;' in f)])),
        (NewDataFrame['EventType'].isin([g for g in NewDataFrame['EventType'] if ('Pattern A1 ; 4 Responsive Therapies' in g or 'Pattern A1 ; 4 Responsive Therapies; Insufficient Charge;' in g)])),
        (NewDataFrame['EventType'].isin([j for j in NewDataFrame['EventType'] if ('Pattern A1 ; 5 Responsive Therapies' in j or 'Pattern A1 ; 5 Responsive Therapies; Insufficient Charge;' in j)])),
        (NewDataFrame['EventType'].isin([k for k in NewDataFrame['EventType'] if ('Pattern A1 Therapy Delivery Inhibited by' in k)])),
        (NewDataFrame['EventType'].isin([l for l in NewDataFrame['EventType'] if ('Pattern A2 ; 1 Responsive Therapy' in l or 'Pattern A2 ; 1 Responsive Therapy; Insufficient Charge;' in l)])),
        (NewDataFrame['EventType'].isin([m for m in NewDataFrame['EventType'] if ('Pattern A2 ; 2 Responsive Therapies' in m or 'Pattern A2 ; 2 Responsive Therapies; Insufficient Charge;' in m)])),
        (NewDataFrame['EventType'].isin([n for n in NewDataFrame['EventType'] if ('Pattern A2 ; 3 Responsive Therapies' in n or 'Pattern A2 ; 3 Responsive Therapies; Insufficient Charge;' in n)])),
        (NewDataFrame['EventType'].isin([o for o in NewDataFrame['EventType'] if ('Pattern A2 ; 4 Responsive Therapies' in o or 'Pattern A2 ; 4 Responsive Therapies; Insufficient Charge;' in o)])),
        (NewDataFrame['EventType'].isin([p for p in NewDataFrame['EventType'] if ('Pattern A2 ; 5 Responsive Therapies' in p or 'Pattern A2 ; 5 Responsive Therapies; Insufficient Charge;' in p)])),
        (NewDataFrame['EventType'].isin([q for q in NewDataFrame['EventType'] if ('Pattern A2 Therapy Delivery Inhibited by' in q)])),
        (NewDataFrame['EventType'] == 'Magnet applied')]
    #Create a list of the values we want to assign for each condition
    valuesT = ['1', '2', '3', '4', '5', '0', '1', '2', '3', '4', '5', '0', '0']

    #Create a new column and use np.select to assign values to it using our lists as arguments
    NewDataFrame['Pattern_A1'] = np.select(conditionsA1, valuesA1)
    NewDataFrame['Pattern_A2'] = np.select(conditionsA2, valuesA2)
    NewDataFrame['Pattern_B1'] = np.select(conditionsB1, valuesB1)
    NewDataFrame['Pattern_B2'] = np.select(conditionsB2, valuesB2)
    NewDataFrame['Therapies'] = np.select(conditionsT, valuesT)

    FinalDataFrame = NewDataFrame.copy().reset_index(drop=True)
    del NewDataFrame
    return FinalDataFrame

## END OF CODE ##
