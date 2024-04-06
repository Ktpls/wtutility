from macroutility import *
import functools


def main():
    hotkeyaction = []

    def swing(t):

        def mydelay():
            time.sleep(0.1)

        mouse.down(0)
        mydelay()
        swingx = 100
        swingy = 100
        for i in range(t):
            mouse.movr(-swingx, -swingy)
            mydelay()
            mouse.movr(swingx, swingy)
            mydelay()
        mouse.up(0)

    #short
    hotkeyaction.append(
        HotkeyManager.hotkeytask(key=win32con.VK_F1,
                                 foo=functools.partial(swing, t=11)))

    #long
    hotkeyaction.append(
        HotkeyManager.hotkeytask(key=win32con.VK_F2,
                                 foo=functools.partial(swing, t=30)))

    mainloop(10, hotkeyaction)


main()