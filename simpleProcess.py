import numpy as np
import cv2 as cv
m=cv.imread(r"C:\prog\wtutility\asset\wtdistmeaspy\yellowmarkBinary.png")
m=cv.cvtColor(m,cv.COLOR_BGR2GRAY).astype(np.float32)/255
m=(m>0.5).astype(np.float32)
cv.imwrite(r"C:\prog\wtutility\asset\wtdistmeaspy\yellowmarkBinary2.png",m*255)