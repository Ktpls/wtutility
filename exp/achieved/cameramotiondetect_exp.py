from math import *
import numpy as np
from scipy.optimize import minimize
from scipy import integrate
import cv2 as cv
import os

OUTPUT_ROOT=r'D:\output\pycammot'
saveidx=0

def savemat(mat):
    global saveidx
    cv.imwrite(os.path.join(OUTPUT_ROOT,'{}.png'.format(saveidx)),mat)
    saveidx+=1

def savematflt(m):
    savemat(256*m)

def spanMat(m,span):
    return cv.GaussianBlur(m,[span,span],0)

def vecMod(v):
    v=np.array(v,np.float32)
    return (v*v).sum()

def matshift(m,o):
    return cv.warpAffine(m,np.array([
    [1,0,o[0]],
    [0,1,o[1]]
    ], np.float32),[m.shape[1],m.shape[0]])

def evaluateOffset(a,b,o):
    relCof=1
    a=matshift(a,o)
    return (a*b).sum()


MATSIZE=500
OFFS=[100,150]
m0=cv.imread(r"D:\output\pycammot\-7ddf286a6cb96653.png")
#m0=cv.imread(r"D:\output\pycammot\0.bmp")
m0=cv.cvtColor(m0,cv.COLOR_BGR2GRAY)
m0=np.array(m0,np.float32)/256

m1=matshift(m0,OFFS)

def feature_polarize_effect(m):
    max=m.max()
    min=m.min()
    ppv=max-min
    if ppv<0.0001:
        ppv=1
    m=(m-min)/ppv
    m=m**5
    return m
m0=feature_polarize_effect(m0)
m1=feature_polarize_effect(m1)

m0=spanMat(m0,200+1)
m1=spanMat(m1,200+1)
savematflt(m0)
savematflt(m1)

def f(X):
    return -evaluateOffset(m0,m1,X)

def pf(X):
    dX=[[1,0],[0,1]]
    fX=f(X)
    X=np.array(X,np.float32)
    return [(f(X+dx)-f(X))/vecMod(dx) for dx in dX]

result =minimize(f,[0,0],method='BFGS',options={'eps':[1,1]})
print(result)