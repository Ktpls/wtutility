from utilref import *

datasource = r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\welllabeled\lbl'
destination = r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\hardones\lbl"
itemfilter = r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\hardones\spl'


def CopyAToBIfInC(A, B, C):
    A = AllFileIn(A)
    C = [os.path.basename(f) for f in AllFileIn(C)]
    for src in A:
        name = os.path.basename(src)
        if name in C:
            os.system(f'copy {src} {os.path.join(B,name)}')


CopyAToBIfInC(datasource, destination, itemfilter)