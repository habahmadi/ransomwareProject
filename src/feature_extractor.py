# this turns the event log into features for the ML model
# for each event I look at what happened in the last few seconds before it

import os
import pandas as pd
import sys

# import honeyfile names so it can be detected when there is activity or when they are touched
# this is needed when feature_extractor is imported from outside src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from honeyfiles import HONEY_NAMES

# find the log file
cur = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(cur)
LOG_FILE = os.path.join(root, "logs", "file_events.csv")

# how many seconds back each window looks
window_secs = 5


def load_events(path=LOG_FILE):
    # read csv and parse timestamp
    # path is optional, so defaults to the live log file
    df = pd.read_csv(path)
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
    num_created = (window["event_type"] == "created").sum()
    num_modified = (window["event_type"] == "modified").sum()
    num_deleted = (window["event_type"] == "deleted").sum()
    num_renamed = (window["event_type"] == "moved_or_renamed").sum()

    # count how many renames ended in .locked since ransomware does this
    # fillna("") so it doesnt crash on empty cells
    dest = window["dest_path"].fillna("").astype(str).str.lower()
    num_locked = dest.str.endswith(".locked").sum()

    # how many unique files were handled in this window
    unique_files = window["file_path"].nunique()

    # check if any honeyfile got touched in this window
    paths = window["file_path"].fillna("").astype(str)
    honey_touched = 0
    for h in HONEY_NAMES:
        if paths.str.contains(h, regex=False).any():
            honey_touched = 1
            break

    return {
        "total_events": total,
        "num_created": num_created,
        "num_modified": num_modified,
        "num_deleted": num_deleted,
        "num_renamed": num_renamed,
        "num_locked_ext": num_locked,
        "unique_files": unique_files,
        "honey_touched": honey_touched,
    }


def build_features(path, label):
    # load events from this specific file
    df = load_events(path)

    # build feature row for every event
    rows = []
    for i in range(len(df)):
        w = get_window_events(i, df)
        feats = extract_features(w)
        feats["timestamp"] = df.loc[i, "timestamp"]
        # label each row
        feats["label"] = label
        rows.append(feats)

    return pd.DataFrame(rows)

if __name__ == "__main__":

    # paths to the two labelled datasets
    normal_path = os.path.join(root, "logs", "normal_events.csv")
    ransom_path = os.path.join(root, "logs", "ransomware_events.csv")

    # extract features from both
    # 0 = normal, 1 = ransomware
    print("Extracting features from normal events...")
    normal_df = build_features(normal_path, 0)
    print("Got", len(normal_df), "normal feature rows")

    print("Extracting features from ransomware events...")
    ransom_df = build_features(ransom_path, 1)
    print("Got", len(ransom_df), "ransomware feature rows")

    # stick them together into one big training dataset
    combined = pd.concat([normal_df, ransom_df], ignore_index=True)

    # and then save it
    out_path = os.path.join(root, "logs", "training_data.csv")
    combined.to_csv(out_path, index=False)

    print("Saved", len(combined), "total rows to", out_path)