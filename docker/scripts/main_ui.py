"""
Script for managing user input for batch service
- modifying config file
- running batch service 
"""

from colorama import init, Fore, Style, Back
import os
import time
import re
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


def bold(text: str) -> str:
    return Style.BRIGHT + text + Style.RESET_ALL


def italic(text: str) -> str:
    return "\033[3m" + text + Style.RESET_ALL


def color(text: str, color: Fore) -> str:
    return color + text + Style.RESET_ALL


def try_convert(value, t):
    try:
        return t(value) > 0
    except (ValueError, TypeError):
        return False


def retry(file, message):
    print(italic(file) + message)
    retry = input("Do you want to retry [" + bold("Y") + "/n]\t")
    return (retry.lower() != "n") and (retry.lower() != "no")


def ask(
    text: str,
    retry_message: str,
    input_type: callable,
    default: object,
    check_type: callable = try_convert,
) -> object:
    user_input = input(text)
    # is default
    if user_input == "":
        print("\033[F\033[K", end="")
        print("using default value: " + bold(str(default)))
        return default
    elif check_type(user_input, input_type):
        return input_type(user_input)
    else:
        if retry(user_input, retry_message):
            ask(text, retry_message, input_type, default, check_type)
        else:
            print("using default value: " + bold(str(default)))
            return default


def infile_listener():  # TODO timeout
    def check_file_exists():
        files = [f for f in os.listdir(output_dir) if re.match(f"^infile.*\\.csv$", f)]
        if files:
            return False, files[0]  # Or perform any other action when the file is found
        return True, []

    if check_file_exists()[0]:
        print("Please move your infile (infile*.csv) to the volume!")
    else:
        file = check_file_exists()[1]
        print(f"Using file: {file}")
        return file
    while check_file_exists()[0]:
        print("-", end="\r")
        time.sleep(0.5)
        print("/", end="\r")
        time.sleep(0.5)
        print("-", end="\r")
        time.sleep(0.5)
        print("\\", end="\r")
        time.sleep(0.5)
    file = check_file_exists()[1]
    print(f"Using file: {file}")
    return file


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
        time.sleep(0.2)
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
    assert type(bit_scores[0]) == float and len(bit_scores) == 2
    # threads 2 x n?
    threads = ask(
        "please define the " + bold("number of threads [1]") + "\n",
        " is not a valide integer",
        int,
        1,
    )
    print("")
    assert type(threads) == int
    if (threads % 2) == 0:
        # adapt monomer config
        config = read_config_file(monomer_config)
        config["environment"]["cores"] = 2
        write_config_file(config, monomer_config)  # TODO
    # download databases
    download = ask(
        "Do you want to "
        + bold("re-download all databases " + "[" + bold("Y") + "/n]\n"),
        " is not a valide value. try " + bold("Y") + "/n",
        lambda x: x,
        "Y",
        lambda x, y: type(x) == str and not try_convert(x, float),
    )
    assert type(download) == str
    if (download.lower() != "no") and (download.lower() != "n"):
        print("Downloading databases")
        os.system("bash " + "/utils/download_db.sh")
    else:
        print("Reusing existing databases\n")
    # wait for infile # TODO change to flag variable
    infile = infile_listener()
    print("")
    assert type(infile) == str
    # modules # TODO backend
    modules = ask(
        "Select which modules to run: "
        + bold("[1, 3, 5]")
        + "\n"
        + bold("1")
        + "\talign\n"
        + "2"
        + "\tconcatenate\tgenome_distance\n"
        + bold("3")
        + "\tconcatenate\tbest_hit\n"
        + "4"
        + "\tconcatenate\tinter_species\n"
        + bold("5")
        + "\tcouplings\n",
        " is not a valide value. try e.g.: 1, 3, 5",
        lambda x: [int(v) for v in x.split(",")],
        [1, 3, 5],
        lambda x, y: type(x.split(",")) == list
        and all([try_convert(v, int) for v in x.split(",")]),
    )
    print("")
    assert type(modules) == list and type(modules[0]) == int
    # Stages
    stages = EVStages(
        output_dir, infile, monomer_config, complex_config, bit_scores, threads
    )
    # Align
    print("\t**************************************")
    print("\t*                                    *")
    print(f"\t*       {color(color=Fore.GREEN, text='1) Phase aligning')}            *")
    print("\t*                                    *")
    # print("\t**************************************\n")
    stages.aligning()
    # Concat / Coupling
    # print("\t**************************************")
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.YELLOW, text='2) Phase couplings')}           *"
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
    swim_whale(31)


main()
