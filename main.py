import os
import sys

from flask import Flask, send_from_directory

cwd = os.getcwd()
app = Flask(__name__, static_url_path=cwd)

# fix for goacess debian package bug https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=934121
@app.route('/fonts/<path:path>')
def send_js(path):
    return send_from_directory(os.path.join(cwd,'fonts'), path)

@app.route('/')
def root():
    try:
        t = os.system('goaccess /var/log/nginx/access.log -o stats_report.html --log-format=COMBINED')
        return send_from_directory(cwd, "stats_report.html")
    except:
        return "No stats."

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 34534
    app.run(port=port, debug=True)