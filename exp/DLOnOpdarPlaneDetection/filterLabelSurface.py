src=r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\all'
dst=r'C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\surffiltered'
import nntracker_common
import os
dataset=nntracker_common.labeldataset().init(src,os.path.join(src,'all.xlsx'),0)
for i in range(dataset.rawlength()):
    spl,lbl=dataset.rawgetitem(i)
    if lbl.sum()>50:
        name=dataset.getname(i)
        print(name)
        a=os.path.join(src,f"spl\\{name}")
        b=os.path.join(dst,f"spl\\{name}")
        os.system(f'copy {a},{b}')
        a=os.path.join(src,f"lbl\\{name}")
        b=os.path.join(dst,f"lbl\\{name}")
        os.system(f'copy {a},{b}')