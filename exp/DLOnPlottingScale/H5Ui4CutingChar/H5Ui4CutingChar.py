
import base64
import time
import threading
import json
import flask
from utility import *
import pytesseract.pytesseract as ptact
tesseractpath = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
app = flask.Flask(__name__)


@app.route("/")
def root():
    return flask.render_template("main.html")


class CharCutter:
    def __init__(self, path) -> None:
        m = cv.imread(path)
        self.m=m[:,:,0]
        self.path = path

    def readpngdata(self):

        with open(self.path, mode='rb') as f:
            data = f.read()
        return data

    def cut(self, start):
        import re

        def safename(name):
            return re.sub('[\\\\/:*?"<>|\r\n]', '-', name)

        def autolabel(m):
            m = np.pad(m, 3, 'constant', constant_values=(0, 0))
            label = ptact.image_to_string(
                m.astype('uint8'), lang='eng', config='--psm 7')
            label = label.replace('\r', '').replace('\n', '')
            return label

        def islabeldigit(l):
            return l in \
                [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "0",
                ]

        charw, charh = 10, 20

        def cutchar(m, start):
            start=int(start)
            return m[:, start:start+charw]

        char = cutchar(self.m, start)
        label = safename(autolabel(char))
        savepath = rf'./output/wtdmp_noised_scale_collection_project/labeled/{label}/' \
            if islabeldigit(label) else \
            rf'./output/wtdmp_noised_scale_collection_project/labeled/else/'
        savemat(char, path=savepath, name=label)
        return {'out': None}


filepath = r"C:\file\code\wtutility\asset\wtdistmeaspy\log\2022-12-20-22-22-54_NormalTrace\unnamed-32.png"
cc = None


@app.route("/SetCharStart", methods=["POST"])
def SetCharStart():

    if flask.request.method != "POST":
        return {'out': f'Wrong request type {flask.request.method}'}
    pos = flask.request.form.get("pos")
    cc.cut(pos)
    win32api.Beep(500,500)
    return {'out': None}


@app.route("/InitCutter", methods=["GET"])
def InitCutter():
    global cc
    cc = CharCutter(filepath)
    data = cc.readpngdata()
    b64 = base64.b64encode(data).decode(encoding='ascii')
    return {'out': b64}


app.run(port=8080)
