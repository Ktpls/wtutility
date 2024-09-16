from . import autofreshmap_configmap_arbarh as autofreshmap_configmap
from .autofreshmap_config_dell import *
from shared import const as sharedconst
import os

singlechanneleddetection = False
subsampleddetection = True
subsampleddetectionrate = 0.1

dbglog = True
waitafterdone = False

standardSpawnCenterError = 200
standardPointSelectorError = 20

standardMatchThreshold = 0.3
standardMapMatchThreshold = 0.34

zFuncPoint0 = 12 / 255
zFuncPoint1 = 25 / 255

setonwifirecoverthresh = 5

detectpointsimilarity = 0.1

minDelayAfterDisconnected = 2

throwerringetdetector = False
throwerrinmain = True

saveScreenShot = False
saveRate = 0.1


wlanname4netshinterface = "WLAN2"
wlanname4netshwlan = [
    "ChinaNet-pHmm",
    "as20",
    "CMCC-305",
    "CMCC-303",
    "HUAZHU-Hanting",
][0]
enteredMatchButNotShowingMap_persistedTime = 3

AFM_FRESHBR_VEHICLE_LIST_TIMEOUT = 50

musicPath = r"C:\CloudMusic"
player = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"

afmassetroot = "./asset/autofreshmap/"
logscreenpath = os.path.join(sharedconst.collectionPath, "/afm/log/screen")

mapAutoCollection = True
mapAutoCollectionPath = os.path.join(sharedconst.collectionPath, "afm/map")

# going better with screen flashing effect at the begining of the map loading screen, but slower like 0.005804599961265922 to 0.0026458000065758824
useNonLightnessedErrorTolerence = False
NonLightnessedErrorRatio = 0.425
