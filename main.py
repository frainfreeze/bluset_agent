import os
import sys
import json
import io
import base64
import datetime
import time
import requests

from flask import Flask, send_from_directory, jsonify

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from requests.api import get

from apscheduler.schedulers.background import BackgroundScheduler

cwd = os.getcwd()
app = Flask(__name__, static_url_path=cwd)
LOG_FILE = "/var/log/nginx/access.log"
FILE_NAME = "stats_report"

MINUTE =  [0,10,20,30,40,50]
TMP_RPM = [1,1,1,1,1,1]
TMP_LATENCY = [1,1,1,1,1,1]

def get_rpm():
    # TODO: this is not valid rpm, but rather just active conections used as mock data!!!
    r = requests.get("http://127.0.0.1/nginx_status")
    if r.status_code == 200:
        rpm = int(r.text.partition('\n')[0].rsplit(': ', 1)[1])
    else:
        rpm = 0
    return rpm

def get_latency():
    # TODO: this is not valid latency, treat as mock data!
    start = time.time()
    r = requests.get(f"http://google.com")
    roundtrip = time.time() - start 
    return int(roundtrip*1000.0)

def update_values():
    now = datetime.datetime.now()
    MINUTE.insert(0, now.minute)
    MINUTE.pop()

    rpm = get_rpm()
    TMP_RPM.insert(0, rpm)
    TMP_RPM.pop()

    latency = get_latency()
    TMP_LATENCY.insert(0, latency)
    TMP_LATENCY.pop()


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_values, trigger="interval", seconds=600)
scheduler.start()

# fix for goacess debian package bug https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=934121
@app.route("/fonts/<path:path>")
def send_js(path):
    return send_from_directory(os.path.join(cwd,"fonts"), path)

@app.route("/")
def index():
    try:
        t = os.system(f"goaccess {LOG_FILE} -o {FILE_NAME}.html --log-format=COMBINED")
        return send_from_directory(cwd, f"{FILE_NAME}.html")
    except:
        return "No stats."

@app.route("/json")
def json_data():
    try:
        t = os.system("goaccess {LOG_FILE} -o {FILE_NAME}.json --log-format=COMBINED")
        with open(f"{FILE_NAME}.json") as f:
            data = json.load(f)
        return jsonify(data)
    except:
        return "No stats."

def data_img(x,y):
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_aspect(1/5)
    ax.axis('off')
    ax.margins(0,0)
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())
    fig.autofmt_xdate()

    pic_IObytes = io.BytesIO()
    fig.savefig(pic_IObytes, format="png", bbox_inches='tight')
    pic_IObytes.seek(0)
    pic_hash = base64.b64encode(pic_IObytes.read())

    return f"data:image/png;base64, {pic_hash.decode('UTF-8')}"


@app.route("/stats")
def mock_stats():
    """ Mock data. Implement me. """
    rpm = get_rpm()
    rpm_graph = data_img(MINUTE, TMP_RPM)      
    latency_graph = data_img(MINUTE, TMP_LATENCY)

    data = {
        'rpm': {
            'time' : MINUTE,
            'data' : TMP_RPM,
            'current' : rpm,
            'graph': rpm_graph
        },
        'latency': {
            'time' : MINUTE,
            'data' : TMP_LATENCY,
            'graph': latency_graph
        }
    }
    return data

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 34534
    app.run(port=port, debug=True)