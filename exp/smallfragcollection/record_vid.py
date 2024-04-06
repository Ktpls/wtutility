from utilref import *


path = r".\output\wtshot.avi"

screensize = np.array([1920, 1080], np.int32)
fps = 5
vidlen = 10
out_gray = cv.VideoWriter(path, cv.VideoWriter.fourcc(*"XVID"), fps, screensize)
hwnd = 0
ss = screenshoter(hwnd)
fpsm = FpsManager(fps)
timer = perf_statistic().start()
print('start')
while True:
    fpsm.WaitUntilNextFrame()
    if timer.time() > vidlen:
        break
    frame = ss.shotbgr()
    # frame_gray=cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
    out_gray.write(frame)


out_gray.release()
print('end')