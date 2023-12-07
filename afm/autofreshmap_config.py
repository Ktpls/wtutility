from .autofreshmap_configmap_plain import whitelistedmap, specialmapdetectors
from .autofreshmap_config_dell import *

singlechanneleddetection = False
subsampleddetection = True
subsampleddetectionrate = 0.1

log2file = False
dbglog = True
waitafterdone = False

standardSpawnCenterError = 200
standardPointSelectorError = 20

standardMatchThreshold = 0.3
standardMapMatchThreshold = 0.25

setonwifirecoverthresh = 10

detectpointsimilarity = 0.1

minDelayAfterDisconnected = 2

throwerringetdetector = False
throwerrinmain = False

saveScreenShot = False
saveRate = 0.1


wlanname4netshinterface = "WLAN2"
wlanname4netshwlan = ["ChinaNet-pHmm", "as20", "CMCC-305", "HUAZHU-Hanting"][2]

AFM_FRESHBR_VEHICLE_LIST_TIMEOUT = 50

musicPath = r"C:\CloudMusic"
player = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"

afmassetroot = "./asset/autofreshmap/"
logscreenpath = "./asset/autofreshmap/log/screen/"
