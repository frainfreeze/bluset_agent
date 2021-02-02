import os
import sys
import json

from flask import Flask, send_from_directory, jsonify

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

        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 34534
    app.run(port=port, debug=True)
