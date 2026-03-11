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