# importing modules which will be needed for file monitoring

import os                       # used for file paths
import time                     # used to keep monitor running
import csv                      # used to write file events into csv
from datetime import datetime   # used to get date and time of each event for logs

# watchdog used to monitor file system events
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# now we need to getthe path to the test_environment folder
current_dir = os.path.dirname(os.path.abspath(__file__))

# go one level up from root
project_root = os.path.dirname(current_dir)

# path to the folder we want to monitor
WATCH_FOLDER = os.path.join(project_root, "test_environment")

# path to the logs folder
LOG_FOLDER = os.path.join(project_root, "logs")

# path to the csv file where events will be saved
LOG_FILE = os.path.join(LOG_FOLDER, "file_events.csv")

# this function creates the csv file if it does not already exist
def create_log_file():

    # checking to make sure logs folder exists
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    # if csv file does not exist, create it and add headings
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "event_type", "file_path", "dest_path"])

# this function writes each file event into the csv file for later usage
# dest_path is only used for move/rename events, otherwise it stays empty           
def write_to_log(event_type, file_path, dest_path = ""):
    with open(LOG_FILE, "a", newline = "") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), event_type, file_path, dest_path])


# this class describes what to do when these file events happen (create, modify, delete, move)
class MyHandler(FileSystemEventHandler):

    # runs when a new file is created
    # runs when a new file is created
    def on_created(self, event):
        # ignore folder events, we only care about files
        if event.is_directory:
            return
        print("File created:", event.src_path)
        write_to_log("created", event.src_path)

    # runs when a file is modified
    def on_modified(self, event):
        if event.is_directory:
            return
        print("File modified:", event.src_path)
        write_to_log("modified", event.src_path)

    # runs when a file is deleted
    def on_deleted(self, event):
        if event.is_directory:
            return
        print("File deleted:", event.src_path)
        write_to_log("deleted", event.src_path)

    # runs when a file is moved or renamed
    def on_moved(self, event):
        if event.is_directory:
            return
        print("File moved or renamed:", event.src_path, "->", event.dest_path)
        write_to_log("moved_or_renamed", event.src_path, event.dest_path)


# this block of code starts the monitoring
if __name__ == "__main__":

    # create the csv log file before monitoring starts
    create_log_file()

    # now create object from our handler class
    event_handler = MyHandler()

    # create the observer
    observer = Observer()

    # tell observer which folder to watch
    observer.schedule(event_handler, WATCH_FOLDER, recursive = True)

    # now start watching the folder
    observer.start()

    print("Monitoring started...")
    print("Watching folder:", WATCH_FOLDER)

    try:
        # keep program running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # stop monitoring when user presses ctrl + c
        print("\nMonitoring stopped.")
        observer.stop()

    observer.join()