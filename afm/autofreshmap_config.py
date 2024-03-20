from .autofreshmap_configmap_laun import whitelistedmap, specialmapdetectors
from .autofreshmap_config_dell import *

singlechanneleddetection = False
subsampleddetection = True
subsampleddetectionrate = 0.1

dbglog = True
waitafterdone = False

standardSpawnCenterError = 200
standardPointSelectorError = 20

standardMatchThreshold = 0.3
standardMapMatchThreshold = 0.25

setonwifirecoverthresh = 5

detectpointsimilarity = 0.1

minDelayAfterDisconnected = 2

throwerringetdetector = False
throwerrinmain = False

saveScreenShot = False
saveRate = 0.1


wlanname4netshinterface = "WLAN2"
wlanname4netshwlan = ["ChinaNet-pHmm", "as20", "CMCC-305", "CMCC-303", "HUAZHU-Hanting"][0]

AFM_FRESHBR_VEHICLE_LIST_TIMEOUT = 50

musicPath = r"C:\CloudMusic"
player = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"

afmassetroot = "./asset/autofreshmap/"
logscreenpath = "./asset/autofreshmap/log/screen/"
