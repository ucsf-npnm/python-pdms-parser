"""scrap data from programming history
"""

#Import standard libraries
import PyPDF2
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import os
import pathlib

#User-specified inputs
patient_id = 'PR05'
input_dir  = '/userdata/dastudillo/patient_data/stage2'
filename   = 'PR05_programming_summary.php.pdf'
output_dir   = '/userdata/dastudillo/patient_data/stage2'

#Main code
#Open PDF file and extract text from all pages

complete_path = pathlib.Path(input_dir, filename)

with open(complete_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text += page.extract_text()

split_text = text.split('\n')

#Retrieve and format programming timestamps

programming_dates_raw = []
programming_times_raw = []

for line in split_text:
    if ('Jan ' in line) or ('Feb ' in line) or ('Mar ' in line) or ('Apr ' in line) or ('May ' in line) or ('Jun ' in line)\
    or ('Jul ' in line) or  ('Aug ' in line) or  ('Sep ' in line) or  ('Oct ' in line) or  ('Nov ' in line) or  ('Dec ' in line):
        programming_dates_raw.append(line)
        programming_times_raw.append(split_text[split_text.index(line)+1])

hours = [x.split(':')[0] for x in programming_times_raw]
minutes = [x.split(':')[1] for x in programming_times_raw]
seconds = [x.split(':')[2][:2] for x in programming_times_raw]

programming_times = []
for i, j, k in zip(hours, minutes, seconds):
    programming_times.append(i+':'+j+':'+k)

programming_timestamps_raw = []
for i, j in zip(programming_dates_raw, programming_times):
    programming_timestamps_raw.append(i+' '+j)

programming_dates = [datetime.strptime(x, '%b %d, %Y') for x in programming_dates_raw]
programming_timestamps = [datetime.strptime(x, '%b %d, %Y %H:%M:%S') for x in programming_timestamps_raw]

#Retrieve stim settings
electrodes_raw = []
for line in split_text:
    if ('Tx1:(' in line) or (('Days' in line) & ('OFF' in line)):
        electrodes_raw.append(line)

electrodes = []
for line in electrodes_raw:
    if 'Tx1:(' in line:
        electrodes.append(line.split('Tx1:')[1])
    if ('Days' in line) & ('OFF' in line):
        electrodes.append('OFF')

amplitudes_raw = []
for line in split_text:
    if (('Tx1' in line) & ('mA' in line)) or (('Days' in line) & ('OFF' in line)):
        amplitudes_raw.append(line)

amplitudes = []
stim_status = []
for line in amplitudes_raw:
    if ('Tx1' in line) & ('mA' in line):
        amplitudes.append(float(line.split(':')[1].replace(' mA', '')))
        stim_status.append('ON')
    if ('Days' in line) & ('OFF' in line):
        amplitudes.append(0.0)
        stim_status.append('OFF')

frequencies_raw = []
for line in split_text:
    if (('Tx1' in line) & ('Hz' in line)) or (('Days' in line) & ('OFF' in line)):
        frequencies_raw.append(line)

frequencies = []
for line in frequencies_raw:
    if ('Tx1' in line) & ('Hz' in line):
        frequencies.append(float(line.split(':')[1].replace(' Hz', '')))
    if ('Days' in line) & ('OFF' in line):
        frequencies.append(0.0)

pw_raw = []
for line in split_text:
    if (('Tx1' in line) & ('µs' in line)) or (('Days' in line) & ('OFF' in line)):
        pw_raw.append(line)

pw = []
for line in pw_raw:
    if ('Tx1' in line) & ('µs' in line):
        pw.append(int(line.split(':')[1].replace(' µs', '')))
    if ('Days' in line) & ('OFF' in line):
        pw.append(0)

durations_raw = []
for line in split_text:
    if (('Tx1' in line) & ('ms' in line)) or (('Days' in line) & ('OFF' in line)):
        durations_raw.append(line)

durations = []
for line in durations_raw:
    if ('Tx1' in line) & ('ms' in line):
        durations.append(int(line.split(':')[1].replace(' ms', '')))
    if ('Days' in line) & ('OFF' in line):
        durations.append(0)

densities_raw = []
for line in split_text:
    if (('Tx1' in line) & ('µC/cm²' in line)) or (('Days' in line) & ('OFF' in line)):
        densities_raw.append(line)

densities = []
for line in densities_raw:
    if ('Tx1' in line) & ('µC/cm²' in line):
        densities.append(float(line.split(':')[1].replace(' µC/cm²', '')))
    if ('Days' in line) & ('OFF' in line):
        densities.append(0.0)

#Create final dataframe
final_df = pd.DataFrame()
final_df['programming_date'] = programming_dates
final_df['start_pst_timestamp'] = programming_timestamps
final_df['stim_status'] =  stim_status
final_df['elecs_(lead1)(lead2)(can)'] =  electrodes
final_df['amplitude'] =  amplitudes
final_df['frequency'] =  frequencies
final_df['pulsewidth'] =  pw
final_df['burst_duration'] =  durations
final_df['charge_density'] =  densities

#Order from oldest to most recent
final_df_save = final_df.sort_values(by='start_pst_timestamp').reset_index(drop=True)
final_df_save.to_csv(f'{output_dir}/{patient_id}_ProgrammingHistory_MostRecent.csv', index=False)

del final_df
del final_df_save

"""End of code"""