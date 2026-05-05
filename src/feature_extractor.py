# this turns the raw event log into sliding-window features for the ML model
# for each event we look at what happened in the last few seconds before it

import os
import pandas as pd

# find the log file
cur = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(cur)
LOG_FILE = os.path.join(root, "logs", "file_events.csv")

# how many seconds back each window looks
window_secs = 5


def load_events():
    # read csv and parse timestamp
    df = pd.read_csv(LOG_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def get_window_events(idx, df):
    # get the time of the current event and the start of the window
    t = df.loc[idx, "timestamp"]
    start = t - pd.Timedelta(seconds=window_secs)
    # include events from start up to and including current event
    w = df[(df["timestamp"] >= start) & (df["timestamp"] <= t)]
    return w


def extract_features(window):

    total = len(window)

    # count each event type
    # comparing the column to a string returns True/False for each row
    num_created = (window["event_type"] == "created").sum()
    num_modified = (window["event_type"] == "modified").sum()
    num_deleted = (window["event_type"] == "deleted").sum()
    num_renamed = (window["event_type"] == "moved_or_renamed").sum()

    # count how many renames ended in .locked extension (textbook ransomware behaviour)
    # then use fillna("") so we dont crash on empty cells
    dest = window["dest_path"].fillna("").astype(str).str.lower()
    num_locked = dest.str.endswith(".locked").sum()

    # how many unique files were handled in this window
    unique_files = window["file_path"].nunique()

    return {
        "total_events": total,
        "num_created": num_created,
        "num_modified": num_modified,
        "num_deleted": num_deleted,
        "num_renamed": num_renamed,
        "num_locked_ext": num_locked,
        "unique_files": unique_files,
    }


if __name__ == "__main__":
    df = load_events()
    print("Loaded", len(df), "events from", LOG_FILE)
    print()

     # for each event, build its feature row from the sliding window
    for i in range(len(df)):
        w = get_window_events(i, df)
        feats = extract_features(w)
        print("Event", i, "->", feats)