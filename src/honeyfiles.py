# this file creates honeyfiles which are decoy files
# they sit in test_environment doing nothing, but if anything touches them
# it should be treated as a strong sign that theres malicious activity

import os

# find the test_environment folder
cur = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(cur)
TEST_FOLDER = os.path.join(root, "test_environment")

# list of honeyfile names
# use a simple list so they can be referenced from other files
HONEY_NAMES = [
    "_AAA_passwords.txt",
    "_AAA_backup_keys.txt",
    "_AAA_financial_records.txt",
]


def create_honeyfiles():
    # first make sure test_environment exists
    if not os.path.exists(TEST_FOLDER):
        os.makedirs(TEST_FOLDER)

    for name in HONEY_NAMES:
        path = os.path.join(TEST_FOLDER, name)
        # only create if it doesnt already exist so we dont accidentally overwrite
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("DO NOT TOUCH - this is a decoy file used for ransomware detection.\n")
            print("Created honeyfile:", path)
        else:
            print("Honeyfile already exists:", path)


if __name__ == "__main__":
    create_honeyfiles()
    print("Done. Honeyfiles created.")