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
from flask import Flask, render_template

# first find the project root
cur = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(cur)

# paths to the csv files written by file_monitor.py
EVENTS_FILE = os.path.join(project_root, "logs", "file_events.csv")
ALERTS_FILE = os.path.join(project_root, "logs", "alerts.csv")

# create the flask app
app = Flask(__name__)


# homepage / main dashboard
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


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