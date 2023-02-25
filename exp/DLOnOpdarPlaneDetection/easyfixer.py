from utilref import *
listfile=r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\sample2fix.xlsx"
PaintDotNet=r"C:\Program Files\paint.net\paintdotnet.exe"
lblpath=r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\all\lbl"
splpath=r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\all\spl"

items=[row[0] for row in Xls2ListList(listfile)]
items=[i for i in items if i is not None]
i=0

while(True):
    filename=items[i]
    print(f'press to open next one, its {filename}')
    os.system('pause')
    os.system(f'"{PaintDotNet}" {os.path.join(splpath,filename)}')
    os.system(f'"{PaintDotNet}" {os.path.join(lblpath,filename)}')
    
    i+=1
    if i >= len(items):
        print('All Done!')
        os.system('pause')
        break