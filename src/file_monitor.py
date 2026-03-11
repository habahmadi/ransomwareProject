# importing modules which will be needed for file monitoring

import os       # used for file paths
import time     # used to keep monitor running

# watchdog used to monitor file system events
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# now we need to getthe path to the test_environment folder
current_dir = os.path.dirname(os.path.abspath(__file__))

# go one level up from root
project_root = os.path.dirname(current_dir)

# path to the folder we want to monitor
WATCH_FOLDER = os.path.join(project_root, "test_environment")


# this class describes what to do when these file events happen (create, modify, delete, move)
class MyHandler(FileSystemEventHandler):

    # runs when a new file is created
    def on_created(self, event):
        print("File created:", event.src_path)

    # runs when a file is modified
    def on_modified(self, event):
        print("File modified:", event.src_path)

    # runs when a file is deleted
    def on_deleted(self, event):
        print("File deleted:", event.src_path)

    # runs when a file is moved or renamed
    def on_moved(self, event):
        print("File moved or renamed:", event.src_path)


# this block of code starts the monitoring
if __name__ == "__main__":

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