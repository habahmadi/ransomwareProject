# creates decoy honeyfiles in test_environment
# if anything touches them its probably ransomware

import os

# find the test_environment folder
cur = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(cur)
TEST_FOLDER = os.path.join(root, "test_environment")

# list of honeyfile names
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
        # only create if it doesnt exist
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("DO NOT TOUCH - this is a decoy file used for ransomware detection.\n")
            print("Created honeyfile:", path)
        else:
            print("Honeyfile already exists:", path)


if __name__ == "__main__":
    create_honeyfiles()
    print("Done. Honeyfiles created.")