import numpy as np
a=np.array([
    [0,1,2,],
    [3,4,5,]
])
a[0,a[0,:]>0]-=1
print(a)