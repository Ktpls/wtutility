import numpy as np
ms=np.array([
    [1,2],
    [3,4],
])
md=np.array([
    [1,2,3],
    [4,5,6],
    [7,8,9],
])

md[1:,1:]=ms
print(md)