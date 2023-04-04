
import sys
sys.path.append(r'.')
import pytesseract.pytesseract as ptact
import numpy as np
import cv2 as cv
from utility import *
from wtdistmeaspy_implementation import cutBottomRightMap, savemat
ptact.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
files = [
    r"C:\Program Files\WarThunder\Screenshots\shot 2022.11.10 21.19.43.png",
    r"C:\Program Files\WarThunder\wtequ\Opdar\output\123abrev.png",
    r"C:\Program Files\WarThunder\wtequ\Opdar\output\170m.png",
    r"C:\Program Files\WarThunder\wtequ\Opdar\output\unnamed-6.png",
]

def density(p,size):
    return regionave(p.astype('float'),size)

def densityfilter(p,size,thresh):
    dence=density(p,size)
    dence[dence<thresh]=0
    return np.logical_and(p, dence)

def map2text():
    m = cv.imread(files[0])
    m = cutBottomRightMap(m)
    savemat(m)
    m = m[-100:, -100:]
    savemat(m)

    #filter color
    hsv=cv.cvtColor(m,cv.COLOR_BGR2HSV)
    darkgraypoints=cv.inRange(hsv,hsv2opencv8bithsv([0,0,0]),hsv2opencv8bithsv([360,40,30]))
    savemat(darkgraypoints)

    #filter adaptive thresh
    m = cv.cvtColor(m, cv.COLOR_BGR2GRAY)
    m = m.astype('float')
    relblack = cv.threshold(
        (m-(regionave(m, [5, 5])-10)), 0, 255, cv.THRESH_BINARY_INV)[1]
    savemat(relblack)
    black = np.logical_and(darkgraypoints, relblack)
    savemat(black*255)
    
    #filter density to remove noise points
    for i in range(4):
        black=densityfilter(black.astype('float'),[5,5],5/25)
        savemat(black*255)
    black=black.astype('uint8')*255
    
    #del the "ruler"
    black[-2:,:]=0
    savemat(black)
    
    #set the most densed pos, as the text is, to center
    dence=density(black,[11,11])
    savemat(dence)
    minval,maxval,minloc,maxloc=cv.minMaxLoc(dence)
    vector=np.flip(dence.shape)*0.5-maxloc
    shiftmat=np.array([
        [1,0,vector[0]],
        [0,1,vector[1]]
    ])
    black=cv.warpAffine(black,shiftmat,np.flip(black.shape))
    savemat(black)
    
    text = ptact.image_to_string(black, lang='eng')
    print(text)


def pic2text():
    m = cv.imread(files[3])

    text = ptact.image_to_string(m)
    print(text)


map2text()
