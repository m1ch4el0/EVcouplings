"""
Script for managing user input for batch service
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
global infile
infile = "/evcomplex/infile.csv"


def bold(text: str) -> str:
    return Style.BRIGHT + text + Style.RESET_ALL


def italic(text: str) -> str:
    return "\033[3m" + text + Style.RESET_ALL


def color(text: str, color: Fore) -> str:
    return color + text + Style.RESET_ALL


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


def check_infile() -> None:
    if not os.path.exists(infile):
        raise FileNotFoundError(
            "PPIs file does not exist. Please check your docker-compose command for flag '-e PPIS=<path-to-input>'"
        )


def select_modules(modules: list) -> None:
    # read configs
    monomer_dict = read_config_file(monomer_config)
    complex_dict = read_config_file(complex_config)
    # modify configs
    for module in modules:
        if module == 1:  # align
            monomer_dict["stages"] = "align"
        elif module == 2:  # genome distance
            complex_dict["stages"] = ["align_1", "align_2", "concatenate"]
            complex_dict["concatenate"]["protocol"] = "genome_distance"
        elif module == 3:  # best hit
            complex_dict["stages"] = ["align_1", "align_2", "concatenate"]
            complex_dict["concatenate"]["protocol"] = "best_hit"
        elif module == 4:  # inter species
            complex_dict["stages"] = ["align_1", "align_2", "concatenate"]
            complex_dict["concatenate"]["protocol"] = "inter_species"
        elif module == 5:  # couplings
            complex_dict["stages"] = ["align_1", "align_2", "concatenate", "couplings"]
        else:
            monomer_dict["stages"] = ""
            complex_dict["stages"] = ""
            raise ValueError("Invalid stage number selected")
    # write files
    write_config_file(monomer_config, monomer_dict)
    write_config_file(complex_config, complex_dict)


def main():
    # print welcome to batch service
    print("\t**************************************")
    print("\t*                                    *")
    print(
        f"\t*       {color(color=Fore.MAGENTA, text='Welcome to EVcomplex!')}        *"
    )
    print("\t*                                    *")
    print("\t**************************************\n")
    # check infile
    check_infile
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
    select_modules(modules)
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


if __name__ == "__main__":
    main()
