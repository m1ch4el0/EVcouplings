"""
Script for batch service with custom config
- modifying config file
- running batch service 
"""

from colorama import init, Fore, Style, Back
import os
import time
from evcouplings.utils.config import read_config_file, write_config_file
import sys

sys.path.insert(0, "/utils")
from stages import EVStages

init()

# global
# variables
global bit_scores
bit_scores = []
global threads
# finals
global monomer_config
monomer_config = "/utils/monomer_config_all.txt"
global complex_config
complex_config = "/utils/complex_config.txt"
global output_dir
output_dir = "/evcomplex/"  # TODO /evcomplex/
global custom_config
custom_config = "/config/custom_config.yaml"
global infile
infile = "/evcomplex/infile.csv"


def bold(text: str) -> str:
    return Style.BRIGHT + text + Style.RESET_ALL


def italic(text: str) -> str:
    return "\033[3m" + text + Style.RESET_ALL


def color(text: str, color: Fore) -> str:
    return color + text + Style.RESET_ALL


def print_whale() -> None:
    top = [
        "                  '",
        '                 ":"',
        '   |"\\/"|     ____:___',
    ]
    bottom = [
        "    \\  /    ,'        '.",
        "    |  \\___/         O  |",
        " ~^~^~^~^~^~^~^~^~^~^~^~^~",
    ]
    for line in top:
        print("\t" + str(line))
    for line in bottom:
        print("\t" + str(line))


def modify_config(config: dict) -> None:
    # config dictionaries
    monomer_dict = read_config_file(monomer_config)
    complex_dict = read_config_file(complex_config)
    # align
    for key in monomer_dict["align"].keys():
        monomer_dict["align"][key] = config["align"][key]
        if key != "reuse_alignment":
            complex_dict["align_1"][key] = config["align"][key]
            complex_dict["align_2"][key] = config["align"][key]
    # concatenate
    for key in complex_dict["concatenate"].keys():
        complex_dict["concatenate"][key] = config["concatenate"][key]
    # couplings
    for key in complex_dict["couplings"].keys():
        complex_dict["couplings"][key] = config["couplings"][key]
    # write configs
    write_config_file(monomer_config, monomer_dict)
    write_config_file(complex_config, complex_dict)


def main():
    # Welcome
    print("\t**************************************")
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.MAGENTA, text='EVcomplex batch service')}        *"
    )
    print("\t*                                    *")
    print("\t**************************************\n")
    # Adapting config # TODO create custom config template
    config = read_config_file(custom_config)
    modify_config(config)
    # Download databases
    if config["utils"]["download"]:
        print("Downloading databases")
        os.system("bash " + "/utils/download_db.sh")
    else:
        print("Reusing existing databases\n")
    # Bit scores
    bit_scores.append(config["align"]["domain_threshold"])
    bit_scores.append(config["align"]["domain_threshold"])
    # Threads
    threads = config["utils"]["threads"]
    # Stages
    stages = EVStages(
        output_dir, infile, monomer_config, complex_config, bit_scores, threads
    )
    # Aligning
    print("\t**************************************")
    print("\t*                                    *")
    print(f"\t*       {color(color=Fore.GREEN, text='1) Stage aligning')}            *")
    print("\t*                                    *")
    # print("\t**************************************\n")
    stages.aligning()
    # Concat / Coupling
    # print("\t**************************************")
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.YELLOW, text='2) Stage couplings')}           *"
    )
    print("\t*                                    *")
    # print("\t**************************************\n")
    stages.couplings()
    # print("\t**************************************")
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.MAGENTA, text='Computations finished')}        *"
    )
    print("\t*                                    *")
    print("\t**************************************\n")
    print_whale()


main()
