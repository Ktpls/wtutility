import numpy as np
import matplotlib.pyplot as plt
class ZFunc:
    def __init__(self,x1,y1,x2,y2) -> None:
        if x1<x2:
            #[lower or higher, x or y]
            self.pt=np.array([[x1,y1],[x2,y2]])
        else:
            self.pt=np.array([[x2,y2],[x1,y1]])
        self.slope=(self.pt[1,1]-self.pt[0,1])/(self.pt[1,0]-self.pt[0,0]+0.0001)
        self.bias=self.pt[0,1]-self.pt[0,0]*self.slope
    def __CallOnNDArray(self,x:np.ndarray):
        y=self.slope*x+self.bias
        y[x<self.pt[0,0]]=self.pt[0,1]
        y[x>self.pt[1,0]]=self.pt[1,1]
        return y
    def __CallOnNum(self,x):
        if x<self.pt[0,0]:
            y=self.pt[0,1]
        elif x>self.pt[1,0]:
            y=self.pt[1,1]
        else:
            y=self.slope*x+self.bias
        return y
    def __call__(self, x):
        if type(x) is np.ndarray:
            return self.__CallOnNDArray(x)
        else:
            return self.__CallOnNum(x)

zfoo=ZFunc(5,0,5+0.01,1)
x=np.linspace(-10,10,100)
y=zfoo(x)
plt.plot(x,y)
plt.show()