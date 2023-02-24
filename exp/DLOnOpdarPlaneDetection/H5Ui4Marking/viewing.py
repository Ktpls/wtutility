import time
import threading
import json
import flask
from operation import *

app = flask.Flask(__name__)


@app.route("/viewing")
def viewingPage():
    return flask.render_template("viewing.html")


filelist = []
oosindex = 0  #indicating next file 2 sample
oos: OperatorOnSample4Viewing = None  # cur char


def auditableMsg():
    win32api.Beep(1000, 250)


def failedMsg():
    win32api.Beep(500, 2000)


@app.route('/NextSample', methods=['GET'])
def NextSample():
    global oosindex, oos, filelist
    if oos is not None:
        oos.finish()
    if oosindex >= len(filelist):
        failedMsg()
        return {'out': '-1'}  # failed

    oos = OperatorOnSample4Viewing(filelist[oosindex])
    data = oos.show()
    oosindex += 1
    auditableMsg()
    return {'out': 1, 'pic': data, 'name': oos.getname()}


@app.route("/InitFileList", methods=["GET"])
def InitFileList():
    global filelist, oos, oosindex
    root = OperatorOnSample4Viewing.SrcPath
    filelist = AllFileIn(root)
    oos = None
    oosindex = 0
    return {'out': None}


app.run(debug=True)
