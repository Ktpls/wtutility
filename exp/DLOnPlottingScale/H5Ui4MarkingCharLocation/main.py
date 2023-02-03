
import base64
import time
import threading
import json
import flask
from utilref import *
app = flask.Flask(__name__)


@app.route("/")
def root():
    return flask.render_template("main.html")


class CharMarker:
    def __init__(self, path) -> None:

        self.path = path

    def readpngdata(self):

        with open(self.path, mode='rb') as f:
            data = f.read()
        return data

    def mark(self, start):
        start=int(start)
        m = cv.imread(self.path)
        m[0, start, -1] = 255

        charw, charh = 10, 20

        name = os.path.basename(self.path)
        savemat(m, path=rf'./output/locmarked/', name=name)
        return {'out': None}


filelist = []
ccindex = -1
cc = None  # cur char


@app.route("/SetCharStart", methods=["POST"])
def SetCharStart():

    if flask.request.method != "POST":
        return {'out': f'Wrong request type {flask.request.method}'}
    pos = flask.request.form.get("pos")
    cc.mark(pos)
    win32api.Beep(500, 500)
    return {'out': None}


@app.route('/NextPic', methods=['GET'])
def NextPic():
    global ccindex
    ccindex += 1
    if ccindex >= len(filelist):
        return {'out': '-1'}  # failed

    global cc
    cc = CharMarker(filelist[ccindex])
    data = cc.readpngdata()
    b64 = base64.b64encode(data).decode(encoding='ascii')
    return {'out': 1, 'pic': b64}


@app.route("/InitFileList", methods=["GET"])
def InitFileList():
    global filelist
    root = r"C:\file\code\wtutility\exp\DLOnPlottingScale\wtdmp_noised_scale_collection_project.202301112304\dedued"
    filelist = AllFileIn(root)
    return {'out': None}


app.run(port=8080)
