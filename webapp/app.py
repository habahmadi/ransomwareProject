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
from flask import Flask, render_template

# first find the project root
cur = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(cur)

# paths to the csv files written by file_monitor.py
EVENTS_FILE = os.path.join(project_root, "logs", "file_events.csv")
ALERTS_FILE = os.path.join(project_root, "logs", "alerts.csv")

# create the flask app
app = Flask(__name__)

def get_summary_stats():
    # builds a dict of high-level numbers for the dashboard top section
    # then wrap them in try/except so the page doesnt crash if a csv is missing

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


def get_events_over_time():
    # groups events by minute so it can plot them as a line chart
    # returns two lists: labels (time strings) and values (event counts)

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
    # counts how many of each event type we have
    # returns labels and values lists for the donut chart

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

# homepage / main dashboard
@app.route("/")
def dashboard():
    stats = get_summary_stats()
    chart_labels, chart_values = get_events_over_time()
    type_labels, type_values = get_event_type_breakdown()
    return render_template(
        "dashboard.html",
        stats=stats,
        chart_labels=chart_labels,
        chart_values=chart_values,
        type_labels=type_labels,
        type_values=type_values,
    )


# alerts page - shows all ML-flagged events
@app.route("/alerts")
def alerts():
    return render_template("alerts.html")


# about page - explains how the system works
@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    # debug=True means the server auto-reloads when code changes
    # which is great and useful during development
    app.run(debug=True, port=5000)