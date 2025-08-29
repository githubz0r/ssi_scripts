import pandas as pd
import os
import re
import functools
#import yaml
import traceback
import sys
import argparse
import numpy as np
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--input_excel", "-i", default = "reads", help = "full path to folder with subfolders containing reads per accession")
#parser.add_argument("--output_folder", "-o", default = "reads_clean", help = "new folder to link the best fastq pair")
args = parser.parse_args()

metadata = pd.read_excel(args.input_excel)
SEQDATA = '/srv/data/SeqData'
ids = []
fastqs_list = []


def search_year_folder(SEQDATA, year, run_substr, sample_id) -> str:
    if year > 2013:
        year_folder = os.path.join(SEQDATA, str(year))
    else:
        year_folder = SEQDATA # no year folder made back then, search runs in seqdata
    run_folder = [i for i in os.listdir(year_folder) if bool(re.search(run_substr, i))]
    print(sample_id, run_folder, 'initial regex search', year)
    if len(run_substr.split('_')) > 1 or len(run_folder) > 1:
        process = subprocess.Popen(f'cd {year_folder}; find . -maxdepth 2 -name \'{sample_id}*\'', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, env=os.environ, encoding='utf-8')
        process_out, process_err = process.communicate()
        #print(process_out, 'das')
        fastqs = [i for i in process_out.split('\n') if len(i) > 0] # remove trailing empty string
        fastqs = [i for i in fastqs if not bool(re.match('.*test', i))] # remove test runs
        fastqs = [i for i in fastqs if not bool(re.match('.*_old', i))] 
        fastqs = [i for i in fastqs if not bool(re.match('.*Qiagen', i))] # probably a test run
        fastqs = [i for i in fastqs if not bool(re.match('.*_fixedrepeat', i))] # weird bifrost frontend output
        fastqs = [i for i in fastqs if not bool(re.match('.*_ITB', i))] # illumina test beads
        fastqs = [i for i in fastqs if not bool(re.match('.*tmp', i))]
        fastqs = [i for i in fastqs if not bool(re.match('.*flex', i))] # hackflex test runs
        fastqs = [i for i in fastqs if not bool(re.match('.*double', i))]
        fastqs = [i for i in fastqs if not bool(re.match('.*copy', i))]
        #fastqs = [i for i in fastqs if not bool(re.match('.*fixed', i))] # weird run but from what I can see the
        fastqs = [i for i in fastqs if bool(re.match(f'.*{sample_id}_', i))] # make sure we are matching the full name of the sample up until underscore
        if len(fastqs) > 2:
            print(f'more than one pair of fastqs for {sample_id}, {fastqs}')
            #print(fastqs)
            run_dates = []
            for i in fastqs:
                _, substr = i.split('./')
                substr_substrings = substr.split('_')
                date = int(substr_substrings[0])
                run_dates.append(date)
            max_date = max(run_dates)
            fastqs = [i for i in fastqs if bool(re.match('.*' + str(max_date), i))] 
        fastqs = ','.join([os.path.join(year_folder, i) for i in fastqs]).replace('./', '')
        #fastqs = ','.join(process_out.split('\n'))
    elif len(run_folder) < 1:
        return '' # no run folder in this year, proceed to next
    else:
        run_folder = os.path.join(year_folder, run_folder[0])
        fastqs = ','.join([os.path.join(run_folder, i) for i in os.listdir(run_folder) if bool(re.search(f'{sample_id}.*fastq', i))])
    #print(run_folder, 'asdf')
    return fastqs

#for i in range(20):
for i in range(metadata.shape[0]):
    fastq_str = ''
    meta_row = metadata.iloc[i,:]
    sample_id = meta_row['ID']
    ids.append(sample_id) # could probably just take it straight from the list but just in case there's some weird indexing going on
    run_substr = str(meta_row['WGS run'])
    year = meta_row['YEAR']
    #print(sample_id)
    while bool(re.match('.*fastq', fastq_str)) == False:
        if year > 2024:
            break
        fastqs = search_year_folder(SEQDATA, year, run_substr, sample_id)
        #print(fastqs)
        fastq_str += fastqs
        year += 1
    fastqs_list.append(fastq_str)
    #print(sample_id, fastq_str)

pd.DataFrame(dict(ID=ids, fastqs=fastqs_list)).to_csv('flemming_fastqs.tsv', sep='\t', index=False)

