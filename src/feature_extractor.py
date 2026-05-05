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


if __name__ == "__main__":
    df = load_events()
    print("Loaded", len(df), "events from", LOG_FILE)
    print()

    # print window size for each event
    for i in range(len(df)):
        w = get_window_events(i, df)
        print("Event", i, "at", df.loc[i, "timestamp"], "-> window has", len(w), "events")