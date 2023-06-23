import cv2 as cv
import torch
import numpy as np
import matplotlib.pyplot as plt
import openpyxl as opx
import os


def Xls2ListList(path=None, sheetname=None, killNones=True):
    if path is None:
        path = r'eles.in.xlsx'
    xls = opx.load_workbook(path)
    if sheetname is None:
        sheet = xls.active
    else:
        sheet = xls[sheetname]

    ret = [[ele.value for ele in ln] for ln in (sheet.rows)]
    if killNones:
        ret = [l for l in ret if any([e is not None for e in l])]
    return ret


def AllFileIn(path, includeFileInSubDir=True):
    import os
    ret = []
    for dirpath, dir, file in os.walk(path):
        if not includeFileInSubDir and dirpath != path:
            continue
        ret.extend([os.path.join(dirpath, f) for f in file])
    return ret


def batchsizeof(tensor):
    return tensor.shape[0]


class nestedPyPlot:

    def __init__(self, outtershape, innershape, fig) -> None:
        self.oshape = np.array(outtershape)
        self.ishape = np.array(innershape)
        self.realsize = self.oshape * self.ishape
        self.fig = fig

    def subplot(self, o, i):
        maincoor = np.array((int(o / self.oshape[1]), o % self.oshape[1]))
        subcoor = np.array((int(i / self.ishape[1]), i % self.ishape[1]))
        realcoor = self.ishape * maincoor + subcoor
        # plt.subplot(self.realsize[0], self.realsize[1], realcoor[0]
        #             * self.realsize[1]+realcoor[1]+1)
        ax = self.fig.add_subplot(
            self.realsize[0], self.realsize[1],
            realcoor[0] * self.realsize[1] + realcoor[1] + 1)
        return ax


def setModel(model, path=None, device='cpu'):
    import os

    if path is None:
        print(f'Path==None')
        return model
    elif not os.path.exists(path):
        print(f'Warning: Path {path} not exist. Set model default')
        return model
    else:
        print(f'Loading existed nn {path}')
        model.load_state_dict(
            torch.load(path, map_location=torch.device(device)))
        #torch.load with map_location=torch.device('cpu')
        return model


def tensorimg2ndarray(m):
    m = np.array(m)
    m = np.moveaxis(m, -3, -1)
    return m
