# handles the remediation side of the system
# when an alert fires a snapshot of the watched folder needs to be preserved
# so the user can recover their files if the attack continues

import os
import shutil
from datetime import datetime

# find the project root
cur = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(cur)

# folder that needs to be backed up
WATCH_FOLDER = os.path.join(root, "test_environment")

# parent folder where all backups go
BACKUPS_FOLDER = os.path.join(root, "backups")


def create_backup():
    # makes a timestamped copy of test_environment

    if not os.path.exists(BACKUPS_FOLDER):
        os.makedirs(BACKUPS_FOLDER)

    # build a folder name using the current time
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(BACKUPS_FOLDER, "backup_" + timestamp)

    # copy the entire watched folder into the backup path
    try:
        shutil.copytree(WATCH_FOLDER, backup_path)
        print("Backup created at:", backup_path)
        return backup_path
    except Exception as e:
        # dont crash the monitor if backup fails, just log and move on
        print("Backup failed:", e)
        return None


if __name__ == "__main__":
    create_backup()