import pandas as pd
import numpy as np
import re
import os, stat, sys
import requests
import glob

#write bsub commands with overwrite
def write_bsub(infile,sampleconfig,output_path):
    file_contents = pd.read_csv(infile)
    #print(file_contents)

    for _,line in file_contents.iterrows():

        protein = line.uid
        r_start = line.region_start
        r_end = line.region_end

        bits_to_use = []
        print(line)

        # Determine if any of the bitscores have already been run,
        # and if so skip them
        for bitscore in list(map(str,[0.2,0.5])):
            # print(bitscore)
            mini_prefix = '{0}_{1}-{2}_b{3}'.format(
                protein,r_start,r_end,bitscore
            )

            final_outcfg_file = '{0}/{1}_final.outcfg'.format(
                output_path,mini_prefix
            )
            config_file = '{0}/{1}/compare/{1}_compare.incfg'.format(
                 output_path,mini_prefix
            )

            if os.path.isfile(final_outcfg_file):
                pass
            else:
                bits_to_use.append(bitscore)

        if len(bits_to_use) > 1:

            os.system('evcouplings -p {0} -r {1}-{2} -b {5} --yolo --prefix {3}/{0}_{1}-{2} {4}'.format(
                    protein,
                    r_start,
                    r_end,
                    output_path,
                    sampleconfig,
                    '\"'+','.join(bits_to_use)+'\"'
            ))

            print('evcouplings -p {0} -r {1}-{2} -b {5} --yolo --prefix {3}/{0}_{1}-{2} monomer_config_all'.format(
                   protein,
                   r_start,
                   r_end,
                   output_path,
                   sampleconfig,
                   '\"'+','.join(bits_to_use)+'\"'
                ))


import sys
_,infile,sampleconfig = sys.argv

config_path=os.path.abspath(sampleconfig)
output_path=os.path.dirname(config_path)+'/output'



write_bsub(infile,sampleconfig,output_path)

