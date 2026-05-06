# importing modules which will be needed for file monitoring

import os                       # used for file paths
import time                     # used to keep monitor running
import csv                      # used to write file events into csv
import joblib
import pandas as pd
from collections import deque
from datetime import datetime   # used to get date and time of each event for logs

# watchdog used to monitor file system events
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# now would need to getthe path to the test_environment folder
current_dir = os.path.dirname(os.path.abspath(__file__))

# go one level up from root
project_root = os.path.dirname(current_dir)

# path to the folder that needs to be monitored
WATCH_FOLDER = os.path.join(project_root, "test_environment")

# path to the logs folder
LOG_FOLDER = os.path.join(project_root, "logs")

# path to the csv file where events will be saved
LOG_FILE = os.path.join(LOG_FOLDER, "file_events.csv")

# path to the trained ML model
MODEL_PATH = os.path.join(project_root, "models", "ransomware_model.pkl")

# load the trained model once when the program starts
# put it in try/except so that the monitor still works if the model isnt trained yet
try:
    model = joblib.load(MODEL_PATH)
    print("Loaded model from", MODEL_PATH)
except FileNotFoundError:
    model = None
    print("WARNING: no trained model found at", MODEL_PATH)
    print("Monitor will run but no ML detection will happen")

# keep up to 200 recent events, anything older then just falls off
# using deque so there is no reason to manually trim a list
recent_events = deque(maxlen=200)

# how many seconds back the live sliding window looks (which matches training)
LIVE_WINDOW_SECS = 5

# track when an alert was last fired so there's no spam
last_alert_time = None
ALERT_COOLDOWN = 10

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


# now build the same 7 features that the model was trained on recently
# but using the live in-memory buffer instead of a saved csv
def get_live_features():
    # if buffer is empty there is nothing to score
    if len(recent_events) == 0:
        return None

    # now work out the cutoff time for the sliding window
    now = datetime.now()
    cutoff = now - pd.Timedelta(seconds=LIVE_WINDOW_SECS)

    # only keep events that happened within the window
    window = [e for e in recent_events if e["timestamp"] >= cutoff]

    if len(window) == 0:
        return None

    # now count up the same things feature_extractor does
    total = len(window)
    num_created = sum(1 for e in window if e["event_type"] == "created")
    num_modified = sum(1 for e in window if e["event_type"] == "modified")
    num_deleted = sum(1 for e in window if e["event_type"] == "deleted")
    num_renamed = sum(1 for e in window if e["event_type"] == "moved_or_renamed")

    # count files renamed to .locked extension
    num_locked = sum(
        1 for e in window
        if e["dest_path"].lower().endswith(".locked")
    )

    # check the number of distinct files in the window
    unique_files = len(set(e["file_path"] for e in window))

    # return as a dict using the SAME column names as training and it has to be in order
    return {
        "total_events": total,
        "num_created": num_created,
        "num_modified": num_modified,
        "num_deleted": num_deleted,
        "num_renamed": num_renamed,
        "num_locked_ext": num_locked,
        "unique_files": unique_files,
    }

# this function checks the latest events against the trained model
def check_for_ransomware():
    # need global because of the reassign last_alert_time below
    global last_alert_time

    if model is None:
        return

    feats = get_live_features()
    if feats is None:
        return

    X = pd.DataFrame([feats])
    prediction = model.predict(X)[0]

    if prediction == 1:
        # check cooldown so alerts are not fired every event
        now = datetime.now()
        if last_alert_time is not None:
            elapsed = (now - last_alert_time).total_seconds()
            if elapsed < ALERT_COOLDOWN:
                return  # still in cooldown, skip

        # fire and remember when
        print("=" * 60)
        print("ALERT: ransomware-like behaviour detected!")
        print("Window features:", feats)
        print("=" * 60)
        last_alert_time = now

# this class describes what to do when these file events happen (create, modify, delete, move)
class MyHandler(FileSystemEventHandler):

    # runs when a new file is created
    def on_created(self, event):
        # ignore folder events, only care about files
        if event.is_directory:
            return
        print("File created:", event.src_path)
        write_to_log("created", event.src_path)
        # add to recent events so the live detector can see it
        recent_events.append({
            "timestamp": datetime.now(),
            "event_type": "created",
            "file_path": event.src_path,
            "dest_path": "",
        })
        check_for_ransomware()

    # runs when a file is modified
    def on_modified(self, event):
        if event.is_directory:
            return
        print("File modified:", event.src_path)
        write_to_log("modified", event.src_path)
        recent_events.append({
            "timestamp": datetime.now(),
            "event_type": "modified",
            "file_path": event.src_path,
            "dest_path": "",
        })
        check_for_ransomware()

    # runs when a file is deleted
    def on_deleted(self, event):
        if event.is_directory:
            return
        print("File deleted:", event.src_path)
        write_to_log("deleted", event.src_path)
        recent_events.append({
            "timestamp": datetime.now(),
            "event_type": "deleted",
            "file_path": event.src_path,
            "dest_path": "",
        })
        check_for_ransomware()

    # runs when a file is moved or renamed
    # record both old (src) and new (dest) paths because ransomware
    # often renames files to .locked which I want to detect
    def on_moved(self, event):
        if event.is_directory:
            return
        print("File moved or renamed:", event.src_path, "->", event.dest_path)
        write_to_log("moved_or_renamed", event.src_path, event.dest_path)
        recent_events.append({
            "timestamp": datetime.now(),
            "event_type": "moved_or_renamed",
            "file_path": event.src_path,
            "dest_path": event.dest_path,
        })
        check_for_ransomware()


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