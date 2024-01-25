"""
Script for managing user input for batch service
- modifying config file
- running batch service 
"""
from colorama import init, Fore, Style, Back
import os
import time

init()

def bold(text):
    return Style.BRIGHT + text + Style.RESET_ALL

def italic(text):
    return "\033[3m" + text + Style.RESET_ALL

def color(text, color):
    return color + text + Style.RESET_ALL

def file_not_found(file):
    print("File '" + italic(file) + "' was not found")
    retry = input("Do you want to retry [" + bold("Y") +"/n]\t")
    if retry.lower() == "n" or retry.lower == "no":
        # TODO quit()
        exit
    else:
        return True

def ask(text, func):
    file = input(text)

    if  os.path.exists(file):
        # TODO merge infiles
        pass
        func()
    else:
        if file_not_found(file):
            ask(text, func)

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
    # batch config file
    #ask("please provide your " + bold("config file") + "\n", lambda x: x)
    print("")
    # batch proteins
    #ask("please provide your " + bold("PPI file [.csv/.tsv]" + "\n"), lambda x: x)
    print("")
    # threads
    #ask("please define the " +  bold("number of threads" + "\n"), lambda x: x)
    print("")
    #
    print("\t**************************************")
    print("\t*                                    *")
    print(f"\t*       {color(color=Fore.MAGENTA, text="calculations started")}         *")
    print("\t*                                    *")
    print("\t**************************************\n")
    swim_whale(27)



main()
