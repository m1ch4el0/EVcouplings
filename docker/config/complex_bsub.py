import pandas as pd
import numpy as np
import re
import os, stat, sys
import requests
import glob
from evcouplings.utils import read_config_file, write_config_file, verify_resources
import time
import ruamel.yaml as yaml


def make_config(line, sampleconfig):
    subprefix = line.prefix
    uniprot1 = line.uid1
    bitscore1 = line.bit1
    region_start1 = line.r_start_1
    region_end1 = line.r_end_1
    aln_prefix1 = line.aln1
    uniprot2 = line.uid2
    bitscore2 = line.bit2
    region_start2 = line.r_start_2
    region_end2 = line.r_end_2
    aln_prefix2 = line.aln2

    config = read_config_file(sampleconfig, preserve_order=True)

    prefix = "output/" + subprefix

    config["global"]["prefix"] = prefix

    # modify the monomer alignment information
    def _monomer_alignments(
        config, namestr, uniprot1, bitscore1, region_start1, region_end1, aln_prefix
    ):
        config[namestr]["sequence_id"] = uniprot1
        config[namestr]["domain_threshold"] = float(bitscore1)
        config[namestr]["sequence_threshold"] = float(bitscore1)
        config[namestr]["region"] = [int(region_start1), int(region_end1)]
        config[namestr]["first_index"] = int(region_start1)
        config[namestr]["input_alignment"] = aln_prefix + ".a2m"
        config[namestr]["override_annotation_file"] = aln_prefix + "_annotation.csv"

        return config

    config = _monomer_alignments(
        config, "align_1", uniprot1, bitscore1, region_start1, region_end1, aln_prefix1
    )
    config = _monomer_alignments(
        config, "align_2", uniprot2, bitscore2, region_start2, region_end2, aln_prefix2
    )

    # quick and dirty alignment size calculation
    if "couplings" in config["stages"]:
        L = (
            int(region_end1)
            - int(region_start1)
            + int(region_end2)
            - int(region_start2)
        )
        q = 20
        memory_in_MB = (1 / 2 * q**2 * (L - 1) * L + q * L) / 12500
        memory_in_MB = max(500, memory_in_MB)
        config["environment"]["memory"] = int(memory_in_MB)

        # hardcode heuristic memory requirements
        if memory_in_MB < 1500:
            config["environment"]["queue"] = "short"
            config["environment"]["time"] = "0-2:0:0"
            # print("submitting to short queue")

        else:
            config["environment"]["queue"] = "short"
            config["environment"]["time"] = "0-3:59:0"
    else:
        config["environment"]["memory"] = 15000
        config["environment"]["queue"] = "short"
        config["environment"]["time"] = "0-5:00:0"
    config["compare"]["plot_model_cutoffs"] = [
        float(x) for x in config["compare"]["plot_model_cutoffs"]
    ]

    return config


# write bsub commands with overwrite
def write_bsub(infile, sampleconfig, output_path):
    # file_contents = pd.read_csv(infile,skiprows=10,nrows=290)
    file_contents = pd.read_csv(infile)
    file_contents = file_contents.head(18840)
    file_contents = file_contents.tail(10000)

    for _, line in file_contents.iterrows():
        print(line)
        subprefix = line.prefix
        config = make_config(line, sampleconfig)

        config_filename = f"output/{subprefix}.txt"
        print(config["compare"]["plot_model_cutoffs"])
        with open(config_filename, "w") as f:
            f.write(
                yaml.dump(config, Dumper=yaml.RoundTripDumper, default_flow_style=False)
            )

        print(f"evcouplings {config_filename}")
        os.system(f"evcouplings --yolo {config_filename}")
        # sbatch -p short -t 0-0:10:0 --mem 20M --mail-type=END --wrap 'evcouplings --yolo {config_filename}'


import sys

_, infile, sampleconfig = sys.argv

output_path = "output/"

write_bsub(infile, sampleconfig, output_path)
