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

sys.path.insert(0, "/home/utils")
from stages import EVStages

init()

# global
# variables
global bit_scores
bit_scores = []
global threads
# finals
global monomer_config
monomer_config = "/home/utils/monomer_config_all.txt"
global complex_config
complex_config = "/home/utils/complex_config.txt"
global custom_config
custom_config = "/home/config/custom_config.yaml"
global output_dir
output_dir = "/evcomplex/"
global infile
infile = "/evcomplex/infile.csv"


def bold(text: str) -> str:
    return Style.BRIGHT + text + Style.RESET_ALL


def italic(text: str) -> str:
    return "\033[3m" + text + Style.RESET_ALL


def color(text: str, color: Fore) -> str:
    return color + text + Style.RESET_ALL


def check_exists(file: str, file_name: str, flag: str) -> None:
    if not os.path.exists(file):
        raise FileNotFoundError(
            f"{file_name} file does not exist. Please check your docker-compose "
            + f"command for flag '-e {flag}=<path-to-input>'"
        )


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
    # stages
    if "align" in monomer_dict["stages"]:
        monomer_dict["stages"] = ["align"]
    if "couplings" in complex_dict["stages"]:
        complex_dict["stages"] = ["align_1", "align_2", "concatenate", "couplings"]
    elif "concatenate" in complex_dict["stages"]:
        complex_dict["stages"] = ["align_1", "align_2", "concatenate"]
    # align
    for key in monomer_dict["align"].keys():
        monomer_dict["align"][key] = config["align"][key]
        if key != "reuse_alignment" and key != "protocol":
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
        f"\t*       {color(color=Fore.MAGENTA, text='EVcomplex batch service')}      *"
    )
    print("\t*                                    *")
    print("\t**************************************\n")
    # check for infile
    check_exists(infile, "PPI input", "PPIS")
    # check for custom config
    check_exists(custom_config, "Config", "CONFIG")
    # Adapting config
    config = read_config_file(custom_config)
    modify_config(config)
    # Download databases
    if config["utils"]["download_db"]:
        print("Downloading databases")
        os.system("bash " + "/utils/download_db.sh")
    else:
        print("Reusing existing databases\n")
    # Bit scores
    bit_scores = config["utils"]["bit_scores"]
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
    if "align" in config["stages"]:
        stages.aligning()
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.YELLOW, text='2) Stage couplings')}           *"
    )
    print("\t*                                    *")
    if "concatenate" in config["stages"] or "couplings" in config["stages"]:
        stages.couplings()
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.MAGENTA, text='Computations finished')}        *"
    )
    print("\t*                                    *")
    print("\t**************************************\n")
    print_whale()


if __name__ == "__main__":
    main()
