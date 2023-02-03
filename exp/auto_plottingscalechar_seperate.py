
#%%
#basics
import sys
sys.path.append('..')
from utility import *

import pytesseract.pytesseract as ptact
tesseractpath=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
ptact.tesseract_cmd = tesseractpath

charw,charh=10,20


def showdenseon(m,dense):
    m=np.copy(m)
    m[-1,:-charw+1,2]=dense
    return m

import re
def safename(name):
    return re.sub('[\\\\/:*?"<>|\r\n]','-',name)

def autolabel(m):
    m=np.pad(m,3, 'constant', constant_values=(0,0))
    label=ptact.image_to_string(
        m.astype('uint8'), lang='eng', config='--psm 7')
    label=label.replace('\r','').replace('\n','')
    return label

def cutchar(m,start):
    return m[:,start:start+charw]

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

def calcRightCharRegionDensity(m,x):
    return cutchar(m,x).sum()/(charw*charh)

def isrightregionchar(m,x):
    return calcRightCharRegionDensity(m,x)>0.1
m=cv.imread(r"C:\file\code\wtutility\output\wtdmp_noised_scale_collection_project\black4CNN_150-15.png")
m=m[:,:,0]

#%%
#do labeling
def main():
    
    for x in range(m.shape[1]):
        if isrightregionchar(m,x):
            start=x
            break
    
    ci=0
    while(True):
        x = start+ci*charw
        if not isrightregionchar(m,x):
            break
        char=cutchar(m,x)
        label=safename(autolabel(char))
        if islabeldigit(label):
            savemat(char,path=rf'./output/wtdmp_noised_scale_collection_project/labeled/{label}/')
        else:
            savemat(char,path=rf'./output/wtdmp_noised_scale_collection_project/labeled/else/',name=label)
        ci+=1
main()

#%%
def markDensityOnScaleSample():
    for x in range(m.shape[1]):
        m[-1,x]=calcRightCharRegionDensity(m,x)
    savemat(m)
markDensityOnScaleSample()