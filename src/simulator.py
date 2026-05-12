# importing modules needed for the simulator

import os       # used for file paths
import time     # used to slow down actions
import random   
import sys
from honeyfiles import create_honeyfiles


# getting the path to the test_environment folder
current_dir = os.path.dirname(os.path.abspath(__file__))

# go one level up from src folder
project_root = os.path.dirname(current_dir)

# path to the folder where test files will be created
TEST_FOLDER = os.path.join(project_root, "test_environment")

# makes sure test folder exists (for good practice)
def create_test_folder():
    if not os.path.exists(TEST_FOLDER):
        os.makedirs(TEST_FOLDER)


def clean_test_environment():
    # remove old files but keep the original honeyfiles
    for file_name in os.listdir(TEST_FOLDER):
        file_path = os.path.join(TEST_FOLDER, file_name)
        if os.path.isfile(file_path):
            # keep only the original honeyfiles
            is_original_honeyfile = (file_name.startswith("_AAA_") and not file_name.endswith(".locked"))
            if not is_original_honeyfile:
                os.remove(file_path)
    print("Test environment cleaned (honeyfiles preserved).")

# this function creates a normal test file
def create_file():

    file_name = "normal_file_1.txt"
    file_path = os.path.join(TEST_FOLDER, file_name)

    with open(file_path, "w") as file:
        file.write("This is a normal test file.\n")

    print("Created file:", file_path)

# this function adds more text into an existing file. All of these functions Im creating is to depict normal file behaviour
def modify_file():

    file_name = "normal_file_1.txt"
    file_path = os.path.join(TEST_FOLDER, file_name)

    with open(file_path, "a") as file:
        file.write("This file was edited normally.\n")

    print("Modified file:", file_path)

# this function renames the file
def rename_file():

    old_name = "normal_file_1.txt"
    new_name = "normal_file_renamed.txt"

    old_path = os.path.join(TEST_FOLDER, old_name)
    new_path = os.path.join(TEST_FOLDER, new_name)

    os.rename(old_path, new_path)

    print("Renamed file:", old_path, "to", new_path)


# this function defines actions that represent normal user behaviour
def normal_behaviour():

    # create a normal file
    create_file()
    time.sleep(2)

    # modify it
    modify_file()
    time.sleep(2)

    # create another file with a different name
    other_path = os.path.join(TEST_FOLDER, "notes.txt")
    with open(other_path, "w") as f:
        f.write("some notes\n")
    print("Created file:", other_path)
    time.sleep(2)

    # edit it twice to simulate someone typing
    with open(other_path, "a") as f:
        f.write("more notes\n")
    print("Modified file:", other_path)
    time.sleep(3)

    with open(other_path, "a") as f:
        f.write("even more notes\n")
    print("Modified file:", other_path)
    time.sleep(2)

    # rename the original one
    rename_file()



# this function creates multiple files which will later be used for ransomware testing
# from here on below, the functions should relate to ransomware-like behaviour. the functions above define normal behaviour
# so the two can be differentiated
def create_multiple_files():

    for i in range(1, 6):
        file_name = "victim_file_" + str(i) + ".txt"
        file_path = os.path.join(TEST_FOLDER, file_name)

        with open(file_path, "w") as file:
            file.write("This is a normal user file.\n")

        print("Created file:", file_path)
        time.sleep(1)


# this function simulates ransomware behaviour
# it quickly modifies and renames many files which is typical behaviour for ransomware
def ransomware_attack():

    # loop through every file inside test folder
    for file_name in os.listdir(TEST_FOLDER):

        old_path = os.path.join(TEST_FOLDER, file_name)

        # target victim files AND honeyfiles
        # but skip already-locked files so it doesnt re-lock them in a loop
        if (os.path.isfile(old_path) 
            and (file_name.startswith("victim_file") or file_name.startswith("_AAA_"))
            and not file_name.endswith(".locked")):

            # first read the file (simulating ransomware scanning files)
            with open(old_path, "r") as file:
                data = file.read()

            # then modify the file to simulate encryption
            with open(old_path, "a") as file:
                file.write("This file has been encrypted.\n")

            print("Modified file:", old_path)

            # typical ransomware often changes file extensions after encryption so I'm doing it here as well
            new_name = file_name + ".locked"
            new_path = os.path.join(TEST_FOLDER, new_name)

            os.rename(old_path, new_path)

            print("Renamed file:", old_path, "to", new_path)

            # very small delay to simulate ransomware behaviour
            time.sleep(0.2)


# this function asks the user which simulation they want to run (this menu is temporary for now, just used for testing purposes only)
# can also be called from outside (e.g. flask) by passing args via sys.argv
def choose_simulation():

    # if command line args were passed use those, otherwise ask interactively
    if len(sys.argv) >= 3:
        choice = sys.argv[1]
        rounds = int(sys.argv[2])
        print("Running simulation from CLI args:", choice, "x", rounds)
    else:
        print("Choose simulation type:")
        print("1. Normal behaviour")
        print("2. Ransomware behaviour")
        choice = input("Enter 1 or 2: ")
        rounds = int(input("How many times to run it? "))

    for r in range(rounds):
        print("\n--- Round", r + 1, "---")

        # clean up between rounds so each one starts fresh
        clean_test_environment()

        if choice == "1":
            normal_behaviour()
        elif choice == "2":
            # only recreate honeyfiles for ransomware runs since they get encrypted
            create_honeyfiles()
            create_multiple_files()
            time.sleep(2)
            ransomware_attack()
        else:
            print("Invalid choice")
            return

        time.sleep(1)

# This if block will be changing many times for testing purposes.
if __name__ == "__main__":

    # make sure the test folder exists
    create_test_folder()

    # remove old files from previous runs
    clean_test_environment()

    # ask the user which simulation they want to run
    choose_simulation()