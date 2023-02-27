#%%
from utilref import *
from zipfile import *
f=r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\all.zip"
f=ZipFile(f)
m=f.read(f'spl/0FTQWBY11D.png')
m=np.frombuffer(m,dtype=np.uint8)
m=cv.imdecode(m,1)
plt.imshow(m)
