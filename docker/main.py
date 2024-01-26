"""
Script for managing user input for batch service
- modifying config file
- running batch service 
"""
from colorama import init, Fore, Style, Back
import os
import time

init()

# global variables
global config_monomer
global config_complex
global infile
global threads

def bold(text):
    return Style.BRIGHT + text + Style.RESET_ALL

def italic(text):
    return "\033[3m" + text + Style.RESET_ALL

def color(text, color):
    return color + text + Style.RESET_ALL

def retry(file, message,required=False):
    print(italic(file) + message)
    retry = input("Do you want to retry [" + bold("Y") +"/n]\t")
    if retry.lower() == "n" or retry.lower == "no":
        if required:
            exit()
    else:
        return True

def ask(text, retry_message, is_valide, required=False):
    user_input = input(text)

    if  is_valide(user_input):
        return user_input
    else:
        if retry(user_input, retry_message, required):
            ask(text, retry_message, is_valide)
        else: 
            print(bold("using default values"))
            return ""

def swim_whale(steps):
    def print_whale(top, bottom):
        for line in top:
                print(" " * step + str(line))
        for line in bottom:
                print(" " * step + str(line))
        
    top1 = ["                  \'",
             "                 \":\"",
             "   |\"\\/\"|     ____:___",]
    top2 = ["                  ",
             "                  :",
             "   |\"\\/\"|     ____:___",]
    top3 = ["                  ",
             "               ",
             "   |\"\\/\"|     ____:___",]
    top4 = ["                  ",
             "                 ",
             "   |\"\\/\"|     _______"]
    bottom = ["    \\  /    ,\'        \'.",
              "    |  \\___/         O  |",
              " ~^~^~^~^~^~^~^~^~^~^~^~^~",]
    for step in range(steps):
        if step % 4 == 0:
            print_whale(top4, bottom)
        elif step % 4 == 1:
            print_whale(top3, bottom)
        elif step % 4 == 2:
            print_whale(top2, bottom)
        else:
            print_whale(top1, bottom)
        time.sleep(0.2)
        for i in range(6):  
            print('\033[F\033[K', end='')  # Clears the terminal for a smoother animation
    print_whale(top1, bottom)

def main():
    # print welcome to batch service
    print("\t**************************************")
    print("\t*                                    *")
    print(f"\t*       {color(color=Fore.MAGENTA, text="Welcome to EVcomplex!")}        *")
    print("\t*                                    *")
    print("\t**************************************\n")
    # monomer config file
    config_monomer = ask("please provide your " + bold("monomer config file") + "\n",
                         " is not a valide file",
                         lambda x: os.path.exists(x))
    print("")
    # complex config file
    config_complex = ask("please provide your " + bold("complex config file") + "\n",
                         " is not a valide file",
                         lambda x: os.path.exists(x))
    print("")
    # batch proteins
    infile = ask("please provide your " + bold("PPI file [.csv/.tsv]" + "\n"),
        " is not a valide file",
        lambda x: os.path.exists(x),
        True)
    print("")
    # threads 2x n?
    threads = ask("please define the " +  bold("number of threads") + "\n",
                  " is not a valide number",
                  lambda x: x.isdigit() and x != "0"), #TODO
    print("")
    #
    print("\t**************************************")
    print("\t*                                    *")
    print(f"\t*       {color(color=Fore.GREEN, text="calculations started")}         *")
    print("\t*                                    *")
    print("\t**************************************\n")
    swim_whale(31)



main()
