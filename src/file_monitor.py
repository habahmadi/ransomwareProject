# importing modules which will be needed for file monitoring

import os       # used for file paths
import time     # used to keep monitor running

# watchdog used to monitor file system events
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler