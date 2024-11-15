"""Custom function to scrap pdf files downloaded from PDMS
"""

#Import standard libraries
import PyPDF2
from PyPDF2 import PdfMerger
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import os
import pathlib

#Get list of files specifying folder path and file format as string
def GetFilePaths(FileDirectory):
    FileNames = sorted(filter(lambda x: True if 'pdf' in x else False, os.listdir(FileDirectory)))
    FilePaths = []
    for file in FileNames:
        FilePaths.append(pathlib.Path(FileDirectory,file))
    return FilePaths

#Merge pdf files
def MergeFiles(OUTPUT_DIR, Files):
    #create and instance of PdfFileMerger() class
    merger = PdfMerger()
    #iterate over the list of file paths
    for file in Files:
        #Append PDF files
        merger.append(file)
    #write out the merged PDF
    outpath = pathlib.Path(OUTPUT_DIR, 'merged_reports.pdf')
    merger.write(outpath)
    merger.close()
    return outpath

