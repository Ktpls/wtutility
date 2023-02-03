import numpy as np
m=np.array([
    [[1,2],[1,1]],
    [[1,1],[1,1]],
])
m[m[:,:,0]!=m[:,:,1]]=[255,0]
print(m)