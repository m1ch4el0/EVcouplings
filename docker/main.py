"""
Script for managing user input for batch service
- modifying config file
- running batch service 
"""
from colorama import init, Fore, Style, Back
import os
import time
import pandas as pd
import numpy as np

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
output_dir = ""  # TODO


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
    # get protein info
    PPIs = pd.read_csv(infile)
    proteins = pd.concat(
        PPIs["uid1", "r_start_1", "r_end_1"], PPIs["uid1", "r_start_1", "r_end_1"]
    ).drop_duplicates()
    proteins.columns = ["uid", "r_start", "r_end"]

    # TODO multithreading
    for _, row in proteins.iterrows():
        os.system(
            "evcouplings -p {0} -r {1}-{2} -b {5} --yolo --prefix {3}/{0}_{1}-{2} {4}".format(
                row.uid,
                row.r_start,
                row.r_end,
                output_dir,
                monomer_config,
                '"' + ",".join(bit_scores) + '"',
            )
        )

        print(
            "evcouplings -p {0} -r {1}-{2} -b {5} --yolo --prefix {3}/{0}_{1}-{2} monomer_config_all".format(
                row.uid,
                row.r_start,
                row.r_end,
                output_dir,
                monomer_config,
                '"' + ",".join(bit_scores) + '"',
            )
        )


def couplings():
    pass


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
    # 1) Phase
    print("\t**************************************")
    print("\t*                                    *")
    print(f"\t*       {color(color=Fore.GREEN, text='1) Phase aligning')}            *")
    print("\t*                                    *")
    # print("\t**************************************\n")
    aligning()
    # 2) Phase
    # print("\t**************************************")
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.YELLOW, text='2) Phase couplings')}           *"
    )
    print("\t*                                    *")
    # print("\t**************************************\n")
    couplings()
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
