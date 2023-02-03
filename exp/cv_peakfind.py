
import sys
sys.path.append('.')
from utility import *

def grad_method():
    k=np.array([
        [0, 1,0],
        [1,-4,1], 
        [0, 1,0],
    ])
    #grad, rather than laplacian
    m=cv.imread(r"C:\Program Files\WarThunder\wtequ\Opdar\opencvplayground\cvpeakfind\unnamed-6.png")
    m=cv.cvtColor(m,cv.COLOR_BGR2GRAY).astype('float')
    b=cv.GaussianBlur(m,[21,21],None)
    savemat(b)
    filt=cv.filter2D(b,-1,k)
    filt=((np.abs(m)>0.1)*(np.abs(filt)<1)).astype('int')
    savemat(filt*255)

def gaussiandensity_method():
    m=cv.imread(r"C:\Program Files\WarThunder\wtequ\Opdar\opencvplayground\cvpeakfind\unnamed-5.png")
    m=cv.cvtColor(m,cv.COLOR_BGR2GRAY).astype('float')
    savemat(m)
    b=cv.GaussianBlur(m,[3,3],None)
    savemat(b)
    filt=(m*(b>200)).astype('int')
    savemat(filt)
grad_method()