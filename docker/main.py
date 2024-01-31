"""
Script for managing user input for batch service
- modifying config file
- running batch service 
"""

from colorama import init, Fore, Style, Back
import os
import time
import re
import pandas as pd
import numpy as np

# from evcouplings.utils.config import read_config_file, write_config_file
import multiprocessing

init()

# global
# variables
global bit_scores
bit_scores = []
global threads
# finals
global monomer_config
monomer_config = "/config/monomer_config_all.txt"
global complex_config
complex_config = "/config/complex_config.txt"
global output_dir
output_dir = "/evcomplex/"  # TODO /evcomplex/


def bold(text):
    return Style.BRIGHT + text + Style.RESET_ALL


def italic(text):
    return "\033[3m" + text + Style.RESET_ALL


def color(text, color):
    return color + text + Style.RESET_ALL


def try_convert(value, t):
    try:
        return t(value) > 0
    except (ValueError, TypeError):
        return False


def retry(file, message):
    print(italic(file) + message)
    retry = input("Do you want to retry [" + bold("Y") + "/n]\t")
    return (retry.lower() != "n") or (retry.lower != "no")


def ask(text, retry_message, input_type, default):
    user_input = input(text)
    # is default
    if user_input == "":
        print("using default value: " + bold(str(default)))
        return default
    elif try_convert(user_input, input_type):
        return input_type(user_input)
    else:
        if retry(user_input, retry_message):
            ask(text, retry_message, input_type, default)
        else:
            print("using default value: " + bold(str(default)))
            return default


def aligning(
    infile,
):
    def _run_aligning(uid, r_start, r_end):
        os.system(
            "evcouplings -p {0} -r {1}-{2} -b {5} --yolo --prefix {3}/{0}_{1}-{2} {4}".format(
                uid,
                r_start,
                r_end,
                output_dir + "align/",
                monomer_config,
                '"' + ",".join(bit_scores) + '"',
            )
        )
        print(
            "evcouplings -p {0} -r {1}-{2} -b {5} --yolo --prefix {3}/{0}_{1}-{2} monomer_config_all".format(
                uid,
                r_start,
                r_end,
                output_dir + "align/",
                monomer_config,
                '"' + ",".join(bit_scores) + '"',
            )
        )

    def check_threads():
        if threads % 2:
            return threads / 2
        return threads

    # get protein info
    PPIs = pd.read_csv(infile)
    proteins = pd.concat(
        PPIs["uid1", "r_start_1", "r_end_1"], PPIs["uid1", "r_start_1", "r_end_1"]
    ).drop_duplicates()
    proteins.columns = ["uid", "r_start", "r_end"]

    with multiprocessing.Pool(check_threads) as pool:
        for _, row in proteins.iterrows():
            pool.apply(_run_aligning, args=[row.uid, row.r_start, row.r_end])


def couplings(infile):
    def _make_config(row):
        config = read_config_file(complex_config, preserve_order=True)
        config["global"]["prefix"] = (
            "output/couplings/" + f"{row.uid1}__{row.uid2}_{row.bit1}-{row.bit2}"
        )
        # TODO rename config with known input
        # alignment 1
        config["align_1"]["sequence_id"] = row.uid1
        config["align_1"]["domain_threshold"] = float(row.bit1)
        config["align_1"]["sequence_threshold"] = float(row.bit1)
        config["align_1"]["region"] = [int(row.r_start_1), int(row.r_end_1)]
        config["align_1"]["first_index"] = int(row.r_start_1)
        config["align_1"]["input_alignment"] = (
            "output/align" + f"{row.uid1}_{row.r_start_1}-{row.r_end_1}.a2m"
        )
        config["align_1"]["override_annotation_file"] = (
            "output/align" + f"{row.uid1}_{row.r_start_1}-{row.r_end_1}_annotation.csv"
        )
        # alignment 2
        config["align_2"]["sequence_id"] = row.uid2
        config["align_2"]["domain_threshold"] = float(row.bit2)
        config["align_2"]["sequence_threshold"] = float(row.bit2)
        config["align_2"]["region"] = [int(row.r_start_2), int(row.r_end_2)]
        config["align_2"]["first_index"] = int(row.r_start_2)
        config["align_2"]["input_alignment"] = (
            "output/align" + f"{row.uid2}_{row.r_start_2}-{row.r_end_2}.a2m"
        )
        config["align_2"]["override_annotation_file"] = (
            "output/align" + f"{row.uid2}_{row.r_start_2}-{row.r_end_2}_annotation.csv"
        )
        # quick and dirty alignment size calculation
        if "couplings" in config["stages"]:
            L = (
                int(row.r_end_1)
                - int(row.r_start_1)
                + int(row.r_end_2)
                - int(row.r_start_2)
            )
            q = 20
            memory_in_MB = (1 / 2 * q**2 * (L - 1) * L + q * L) / 12500
            memory_in_MB = max(500, memory_in_MB)
            config["environment"]["memory"] = int(memory_in_MB)  # maybe remove
        config["compare"]["plot_model_cutoffs"] = [
            float(x) for x in config["compare"]["plot_model_cutoffs"]
        ]
        return config

    def _run_couplings(config_filename):
        # run config
        os.system(f"evcouplings --yolo {config_filename}")
        print(f"evcouplings {config_filename}")

    PPIs = pd.read_csv(infile)

    with multiprocessing.Pool(threads) as pool:
        for _, line in PPIs.iterrows():
            # write config
            config = _make_config()
            config_filename = f"output/{line.prefix}.txt"
            print(config["compare"]["plot_model_cutoffs"])
            write_config_file(config, config_filename)
            # run couplings
            pool.apply(_run_couplings, args=config_filename)


def infile_listener():  # TODO timeout
    def check_file_exists():
        files = [f for f in os.listdir(output_dir) if re.match(f"^infile.*\.csv$", f)]
        if files:
            print(f"Using file: {files[0]}")
            return False  # Or perform any other action when the file is found
        return True

    while check_file_exists():
        print("Please move your infile (infile*.csv) to the volume!", end="\r")
        time.sleep(10)


def swim_whale(steps):
    def print_whale(top, bottom):
        for line in top:
            print(" " * step + str(line))
        for line in bottom:
            print(" " * step + str(line))

    top1 = [
        "                  '",
        '                 ":"',
        '   |"\\/"|     ____:___',
    ]
    top2 = [
        "                  ",
        "                  :",
        '   |"\\/"|     ____:___',
    ]
    top3 = [
        "                  ",
        "               ",
        '   |"\\/"|     ____:___',
    ]
    top4 = ["                  ", "                 ", '   |"\\/"|     _______']
    bottom1 = [
        "    \\  /    ,'        '.",
        "    |  \\___/         O  |",
        " ~^~^~^~^~^~^~^~^~^~^~^~^~",
    ]
    bottom2 = [
        "    \\  /    ,'        '.",
        "    |  \\___/         O  |",
        " ^~^~^~^~^~^~^~^~^~^~^~^~^",
    ]
    for step in range(steps):
        if step % 4 == 0:
            print_whale(top4, bottom2)
        elif step % 4 == 1:
            print_whale(top3, bottom1)
        elif step % 4 == 2:
            print_whale(top2, bottom2)
        else:
            print_whale(top1, bottom1)
        time.sleep(0.18)
        for i in range(6):
            print(
                "\033[F\033[K", end=""
            )  # Clears the terminal for a smoother animation
    step += 1
    print_whale(top1, bottom1)


def main():
    # print welcome to batch service
    print("\t**************************************")
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.MAGENTA, text='Welcome to EVcomplex!')}        *"
    )
    print("\t*                                    *")
    print("\t**************************************\n")
    # monomer config file
    bit_scores.append(
        ask(
            "please define the " + bold("first bit score [0.2]") + "\n",
            " is not a valide float",
            float,
            0.2,
        )
    )
    bit_scores.append(
        ask(
            "please define the " + bold("second bit score [0.5]") + "\n",
            " is not a valide float",
            float,
            0.5,
        )
    )
    print("")
    # threads 2 x n?
    threads = ask(
        "please define the " + bold("number of threads [1]") + "\n",
        " is not a valide integer",
        int,
        1,
    )
    print("")
    if (threads % 2) == 0:
        # adapt monomer config
        config = read_config_file(monomer_config)
        config["environment"]["cores"] = 2
        write_config_file(config, monomer_config)
    # wait for infile
    infile = infile_listener()
    # 1) Phase
    print("\t**************************************")
    print("\t*                                    *")
    print(f"\t*       {color(color=Fore.GREEN, text='1) Phase aligning')}            *")
    print("\t*                                    *")
    # print("\t**************************************\n")
    aligning(infile)
    # 2) Phase
    # print("\t**************************************")
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.YELLOW, text='2) Phase couplings')}           *"
    )
    print("\t*                                    *")
    # print("\t**************************************\n")
    couplings(infile)
    # 2) Phase
    # print("\t**************************************")
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.MAGENTA, text='Computations finished')}        *"
    )
    print("\t*                                    *")
    print("\t**************************************\n")
    swim_whale(31)


main()
