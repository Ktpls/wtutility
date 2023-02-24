import time
import threading
import json
import flask
from operation import *

app = flask.Flask(__name__)


@app.route("/marking")
def markingPage():
    return flask.render_template("marking.html")


filelist = []
oosindex = 0  #indicating next file 2 sample
oos: OperatorOnSample = None  # cur char


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

    oos = OperatorOnSample(filelist[oosindex])
    data = OperatorOnSample.readPngData(oos.path)
    oosindex += 1
    auditableMsg()
    return {'out': 1, 'pic': data}


@app.route("/SetPos", methods=["POST"])
def SetPos():
    if flask.request.method != "POST":
        return {'out': f'Wrong request type {flask.request.method}'}
    keys = ['y', 'x']
    pos = [int(flask.request.form.get(key)) for key in keys]
    data = oos.markpos(pos)
    auditableMsg()
    return {'out': data}


@app.route("/SetAdd", methods=["POST"])
def SetAdd():
    if flask.request.method != "POST":
        return {'out': f'Wrong request type {flask.request.method}'}
    data = oos.addthresh()
    print(oos.thresh)
    auditableMsg()
    return {'out': data}


@app.route("/SetMin", methods=["POST"])
def SetMin():
    if flask.request.method != "POST":
        return {'out': f'Wrong request type {flask.request.method}'}
    data = oos.minthresh()
    print(oos.thresh)
    auditableMsg()
    return {'out': data}


@app.route("/InitFileList", methods=["GET"])
def InitFileList():
    global filelist, oos, oosindex
    root = r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\H5Ui4Marking\dataset\unproc"
    filelist = AllFileIn(root)
    oos = None
    oosindex = 0
    return {'out': None}


app.run(debug=True)
