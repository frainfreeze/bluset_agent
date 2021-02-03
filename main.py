import os
import sys
import json
import io
import base64

import requests

from flask import Flask, send_from_directory, jsonify

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

cwd = os.getcwd()
app = Flask(__name__, static_url_path=cwd)
LOG_FILE = "/var/log/nginx/access.log"
FILE_NAME = "stats_report"

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
    rpm_graph = data_img([0,1,2,3,4], [0,0,0,0,0])      
    latency_graph = data_img([0,1,2,3,4], [1,2,1,3,2])

    # TODO: this is not valid rpm, but rather just active conections used as mock data!!!
    r = requests.get("http://127.0.0.1/nginx_status")
    if r.status_code == 200:
        rpm = int(r.text.partition('\n')[0].rsplit(': ', 1)[1])
    else:
        rpm = 0

    data = {
        'rpm': {
            'time' : [0,1,2,3,4],
            'data' : [0,0,0,0,0],
            'current' : rpm,
            'graph': rpm_graph
        },
        'latency': {
            'time' : [0,1,2,3,4],
            'data' : [4,6,2,5,4],
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