# this is the flask web app I mentioned for the ransomware detection dashboard
# it reads the same event and alerts csvs that the monitor writes
# and displays them in a more readable way with charts and stats
#
# flask references:
#   https://flask.palletsprojects.com/en/stable/quickstart/         (quickstart)
#   https://flask.palletsprojects.com/en/stable/tutorial/           (full tutorial)
#   https://jinja.palletsprojects.com/en/stable/templates/          (templates)
#   https://flask.palletsprojects.com/en/stable/patterns/jquery/    (returning JSON for charts)

import os
import pandas as pd
import time
import subprocess
import sys
from flask import Flask, render_template, send_file

# first find the project root
cur = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(cur)

# paths to the csv files written by file_monitor.py
EVENTS_FILE = os.path.join(project_root, "logs", "file_events.csv")
ALERTS_FILE = os.path.join(project_root, "logs", "alerts.csv")
# path to the simulator script
SIMULATOR_SCRIPT = os.path.join(project_root, "src", "simulator.py")

# path to the file monitor script
MONITOR_SCRIPT = os.path.join(project_root, "src", "file_monitor.py")

monitor_process = None

# create the flask app
app = Flask(__name__)

# context processor runs before every template
@app.context_processor
def inject_monitor_status():
    return {"monitor_status": get_monitor_status()}

def get_summary_stats():
    # builds a dict of high-level numbers for the dashboard top section

    # default values in case nothing exists yet
    stats = {
        "total_events": 0,
        "total_alerts": 0,
        "unique_files": 0,
        "model_accuracy": 98.61,  # this is from the model.py training output
    }

    # read events csv
    try:
        events_df = pd.read_csv(EVENTS_FILE)
        stats["total_events"] = len(events_df)
        stats["unique_files"] = events_df["file_path"].nunique()
    except FileNotFoundError:
        pass

    # read alerts csv
    try:
        alerts_df = pd.read_csv(ALERTS_FILE)
        stats["total_alerts"] = len(alerts_df)
    except FileNotFoundError:
        pass

    return stats


def get_honeyfile_status():
    # checks each honeyfile and returns its status for the dashboard

    # the three honeyfile names match what honeyfiles.py creates
    HONEY_NAMES = [
        "_AAA_passwords.txt",
        "_AAA_backup_keys.txt",
        "_AAA_financial_records.txt",
    ]

    watch_folder = os.path.join(project_root, "test_environment")
    statuses = []

    # list whats currently in the watched folder
    try:
        current_files = os.listdir(watch_folder)
    except FileNotFoundError:
        current_files = []

    for name in HONEY_NAMES:
        # .locked version means ransomware got to it
        locked_present = any(f.startswith(name) and f.endswith(".locked") for f in current_files)
        # check if the original file is still there
        original_present = name in current_files

        if locked_present or not original_present:
            statuses.append({"name": name, "status": "compromised"})
        else:
            statuses.append({"name": name, "status": "intact"})

    return statuses

def get_events_over_time():
    # group events by minute for the line chart

    labels = []
    values = []

    try:
        df = pd.read_csv(EVENTS_FILE)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # group by minute and count how many events landed in each bucket
        grouped = df.set_index("timestamp").resample("1min").size()

        # convert to lists for the chart
        labels = [t.strftime("%H:%M") for t in grouped.index]
        values = grouped.tolist()
    except FileNotFoundError:
        pass

    return labels, values

def get_event_type_breakdown():
    # count event types for the donut chart

    labels = []
    values = []

    try:
        df = pd.read_csv(EVENTS_FILE)
        counts = df["event_type"].value_counts()
        labels = counts.index.tolist()
        values = counts.tolist()
    except FileNotFoundError:
        pass

    return labels, values


def get_top_files(limit=10):
    # finds the top N most-touched files
    # returns lists of (basename, count)

    names = []
    counts = []

    try:
        df = pd.read_csv(EVENTS_FILE)
        # group by file path, count rows, sort desc, take top N
        top = df["file_path"].value_counts().head(limit)
        # shorten paths to just the file name so they fit in the panel
        names = [os.path.basename(p) for p in top.index]
        counts = top.tolist()
    except FileNotFoundError:
        pass

    return names, counts


def get_recent_events(limit=20):
    # most recent N events for the table

    rows = []
    try:
        df = pd.read_csv(EVENTS_FILE)
        # sort newest first and take top N
        df = df.sort_values("timestamp", ascending=False).head(limit)
        # turn each row into a dict for a more easier template access
        for _, row in df.iterrows():
            rows.append({
                "timestamp": row["timestamp"],
                "event_type": row["event_type"],
                "file_path": os.path.basename(str(row["file_path"])),
            })
    except FileNotFoundError:
        pass

    return rows


def get_monitor_status():
    if monitor_process is not None and monitor_process.poll() is None:
        return "active"
    return "offline"

def get_alerts():
    # all alerts, newest first

    rows = []
    try:
        df = pd.read_csv(ALERTS_FILE)
        df = df.sort_values("timestamp", ascending=False)
        for _, row in df.iterrows():
            rows.append({
                "timestamp": row["timestamp"],
                "total_events": row["total_events"],
                "num_created": row["num_created"],
                "num_modified": row["num_modified"],
                "num_deleted": row["num_deleted"],
                "num_renamed": row["num_renamed"],
                "num_locked_ext": row["num_locked_ext"],
                "unique_files": row["unique_files"],
                "honey_touched": row["honey_touched"],
            })
    except FileNotFoundError:
        pass

    return rows

# homepage / main dashboard
@app.route("/")
def dashboard():
    stats = get_summary_stats()
    chart_labels, chart_values = get_events_over_time()
    type_labels, type_values = get_event_type_breakdown()
    top_names, top_counts = get_top_files()
    recent_events = get_recent_events()
    honey_status = get_honeyfile_status()
    return render_template(
        "dashboard.html",
        stats=stats,
        chart_labels=chart_labels,
        chart_values=chart_values,
        type_labels=type_labels,
        type_values=type_values,
        top_names=top_names,
        top_counts=top_counts,
        recent_events=recent_events,
        honey_status=honey_status,
    )


# alerts page - shows all ML-flagged events
@app.route("/alerts")
def alerts():
    alerts_list = get_alerts()
    return render_template("alerts.html", alerts=alerts_list)


# about page - explains how the system works
@app.route("/about")
def about():
    return render_template("about.html")

# these are routes that launch the simulator in the background
# I use subprocess.Popen so flask doesnt block waiting for the simulation to finish

@app.route("/run/normal", methods=["POST"])
def run_normal():
    # launch a single round of normal behaviour
    subprocess.Popen([sys.executable, SIMULATOR_SCRIPT, "1", "1"])
    return "ok", 200


@app.route("/run/ransomware", methods=["POST"])
def run_ransomware():
    # launch a single round of ransomware behaviour
    subprocess.Popen([sys.executable, SIMULATOR_SCRIPT, "2", "1"])
    return "ok", 200

@app.route("/monitor/start", methods=["POST"])
def start_monitor():
    # spawn the file monitor as a background subprocess
    global monitor_process

    # if its already running dont start a second one
    if monitor_process is not None and monitor_process.poll() is None:
        return "already running", 200

    monitor_process = subprocess.Popen([sys.executable, MONITOR_SCRIPT])
    return "started", 200


@app.route("/monitor/stop", methods=["POST"])
def stop_monitor():
    # kill the monitor subprocess if its running
    global monitor_process

    if monitor_process is not None and monitor_process.poll() is None:
        monitor_process.terminate()
        monitor_process = None
        return "stopped", 200

    return "not running", 200

# download routes - lets the user save the raw csv files

@app.route("/download/events")
def download_events():
    try:
        return send_file(EVENTS_FILE, as_attachment=True, download_name="file_events.csv")
    except FileNotFoundError:
        return "No events log found", 404


@app.route("/download/alerts")
def download_alerts():
    try:
        return send_file(ALERTS_FILE, as_attachment=True, download_name="alerts.csv")
    except FileNotFoundError:
        return "No alerts log found", 404

if __name__ == "__main__":
    # debug=True so the server reloads on code changes
    app.run(debug=True, port=5000, use_reloader=False)