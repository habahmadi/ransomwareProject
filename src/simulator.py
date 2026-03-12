# importing modules needed for the simulator

import os       # used for file paths
import time     # used to slow down actions
import random   


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


# this function removes old files so its used as a cleanup function
def clean_test_environment():
    for file_name in os.listdir(TEST_FOLDER):
        file_path = os.path.join(TEST_FOLDER, file_name)

        if os.path.isfile(file_path):
            os.remove(file_path)

    print("Test environment cleaned.")

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

        # only target the victim files that were created earlier
        if os.path.isfile(old_path) and file_name.startswith("victim_file"):

            # this part simulates encryption
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


# This if block will be changing many times for testing purposes.
# Before it was testing normal behaviour, now its testing ransoware-like behaviour
if __name__ == "__main__":

    # make sure the test folder exists
    create_test_folder()

    # remove old files so fresh start every time
    clean_test_environment()

    # create victim files that ransomware will target
    create_multiple_files()

    # wait a moment before the attack starts
    time.sleep(2)

    # simulate ransomware behaviour
    ransomware_attack()