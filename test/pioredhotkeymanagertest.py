from utilref import *
import traceback


hotkeyaction = []
def foo1():
    print('f1')
hotkeyaction.append(hotkeymanager.hotkeytask(
    key=win32con.VK_F1,
    foo=foo1
))
def foo2():
    print('ctrl+f1')
hotkeyaction.append(hotkeymanager.hotkeytask(
    key=[win32con.VK_CONTROL,win32con.VK_F1],
    foo=foo2
))

'''
expect:
only foo1() on f1
only foo2() on ctrl+f1
'''
hkm = hotkeymanager(hotkeyaction)
while(True):
    hkm.doAllDecidedKey(hkm.decideAllHotKey())
    print('waiting')
    sleep(1)