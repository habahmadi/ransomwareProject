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

# this function creates a normal test file
def create_file():

    file_name = "normal_file_1.txt"
    file_path = os.path.join(TEST_FOLDER, file_name)

    with open(file_path, "w") as file:
        file.write("This is a normal test file.\n")

    print("Created file:", file_path)

# this simply runs the simulator
if __name__ == "__main__":

    create_file()