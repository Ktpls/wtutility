from utilitypack import rgb2bgr, hsv2rgb, np


def getlambfromtarget(how, where, mu=0):
    return (1 / how - 1) / ((where - mu) ** 2)


# screen
w = 1920
h = 1080

# opdar
fps = 15
stablamb = 0.75
stabaccepterrrelthr = 100  # not used
stabaccepterrabsthr = 60
# tracker
useNnTracker = False
trackFps = 15
camerestablizersubsamplerate = 0.1
planetrackerchannel = "V"
searchrange = 150 // 2  # -sr~+sr, must be 16n. as for sr, must be 8n
backgroundrange = 41
adptthresh = 0.1
abslthresh = 0.1
rhothresh = 0.1
regionrange = 3
posrellamb = getlambfromtarget(0.75, 1) # pos ref not so accurate
wingspanrellamb = getlambfromtarget(0.5, 0.25)
shapereallamb = getlambfromtarget(0.2, 1)
wingspanleast = 5
scoreleast = 0.1
mtiOn = True
mtiQueueSize = 3
# firecontrol
c_thetabypix = 0.8115411412708535 * 1e-3
useThetaByPixCalcFromMil = False
targetwingspan = 16.3e-3
vbullet = 0.580
screensize = np.array([w, h], np.int32)
lockpoint_default = screensize * [0.5, 0.2]
epsilon = 1e-3

# render
lockcirclethickness = 1
innerhue = 180
lockcirclecolorinner = 255 * rgb2bgr(hsv2rgb((innerhue, 0.5, 0.8)))
lockcirclecoloroutter = 255 * rgb2bgr(hsv2rgb((innerhue + 180, 0.5, 0.8)))
lockcirclecolor = 255 * rgb2bgr(hsv2rgb((0, 0, 1)))
firecontrolserieshue = 206 + 180
firecontrolseriesthickness = 2
planecircleradius = 30
planecirclecolor = 255 * rgb2bgr(hsv2rgb((firecontrolserieshue, 0.6, 1)))
speedvectorcolor = 255 * rgb2bgr(hsv2rgb((firecontrolserieshue, 0.6, 1)))
firecontrolcirclecolor = 255 * rgb2bgr(hsv2rgb((firecontrolserieshue, 0.6, 1)))
lineheight = 25
textcolor = 255 * rgb2bgr(hsv2rgb((0, 0, 1)))

# datacollecting
collectingPlaneSample = False
collectingPlaneSampleRate = 0.1

uimaskPath = r"./asset/opdar/UIMASK.png"
datacoll_samplepath = "./output/opdar_plane/"
datacoll_labelpath = "./output/opdar_plane/"
datacoll_sampleFormat="{}.png"
datacoll_labelFormat="{}_mask_0.png"
