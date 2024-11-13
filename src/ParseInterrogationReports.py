##This will contain custom function to scrap pdf files downloaded from PDMS

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

#Import custom functions
from ParserTools import GetFilePaths, MergeFiles, RunParser

#User-specified inputs
patient_id = 'PR05'
start, stop = '20240214_0000', '20240215_0000'
INDIR = '/userdata/dastudillo/patient_data/tmp/'
OUTDIR = '/userdata/dastudillo/patient_data/tmp'

#Main code
fn_merged = f'{patient_id}_{start}-{stop}_merged.pdf'
fn_parsed = f'{patient_id}_{start}-{stop}_parsed.csv'

input_files = GetFilePaths(INDIR, 'pdf')
master_file_path = MergeFiles(OUTDIR, input_files, fn_merged)

tabulated_data = RunParser(master_file_path)
##save new dataframe as csv file
tabulated_data.to_csv(pathlib.Path(OUTDIR, fn_parsed), index=False)

## END OF CODE ##

