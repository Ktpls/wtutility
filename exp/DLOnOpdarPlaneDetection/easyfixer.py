from utilref import *
listfile=r"D:\File\code\prog\wtutility\output\opdar_plane\xls.xlsx"
PaintDotNet=r"C:\Program Files\paint.net\paintdotnet.exe"
lblpath=r"D:\File\code\prog\wtutility\output\opdar_plane\lbl"
splpath=r"D:\File\code\prog\wtutility\output\opdar_plane\spl"

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