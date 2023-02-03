
import sys
sys.path.append('.')
from utility import *

def threshedmatchtemplate(src,temp,mask,simu):
    matchresult=cv.matchTemplate(src,temp,cv.TM_SQDIFF_NORMED,mask=mask)
    minval,maxval,minloc,maxloc=cv.minMaxLoc(matchresult)
    #print(minval)
    return minloc if minval<=simu else None

#find single point on map
def matchOnMap(m,temp,mask,color):
    m=np.copy(m)
    ret=threshedmatchtemplate(m,temp,mask,0.1)
    thickness=2
    if ret is None:
        picsize=np.flip(m.shape[:2])
        cv.line(m,picsize*[0,0],picsize*[1,1],color,thickness)
        cv.line(m,picsize*[0,1],picsize*[1,0],color,thickness)
    else:
        cv.rectangle(m,ret,ret+np.flip(mask.shape),color,thickness)
    return m

files=[
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\AbandonedFactory.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\AbandonedTown.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\AdvanceToTheRhine.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Alaska.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\AmericanDesert.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\AralSea.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\AshRiver.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Battle.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\BattleOfHurtgenForestConquest#1.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\BattleOfHurtgenForestDomination#1.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Berlin.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\BerlinDomination.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Breslau.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Campania.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\CargoPort.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Carpathians.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Conquest.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\EasternEurope.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\FieldsOfNormandy.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Finland.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\FireArc.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\FrozenPass.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Japan.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Japan_reversed.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Jungle.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Karelia.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Kurban.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\MiddleEast.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\MissionCanceled.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Mozdok#1.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Mozdok#2.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Normandy.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Normandy_reversed.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\OK.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Poland.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\PortNovorossiysk.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\PortNovorossiyskBattle.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\PortNovorossiyskConquest#2.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Pradesh.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Serversk-13.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Sinai.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Stalingrad.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\SunCity.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\SurroundingsOfVolokolamsk.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Sweden.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Tunisia.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\rawmaterial\Volokolamsk.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\AbandonedFactory.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\AbandonedTown.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\AdvanceToTheRhine.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Alaska.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\AmericanDesert.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\AralSea.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\AshRiver.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\BattleOfHurtgenForestConquest#1.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\BattleOfHurtgenForestDomination#1.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Berlin.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Breslau.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Campania.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\CargoPort.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Carpathians.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\EasternEurope.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\FieldsOfNormandy.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Finland.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\FireArc.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\FrozenPass.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Japan.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Jungle.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Karelia.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Kurban.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\MiddleEast.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Mozdok#1.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Mozdok#2.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Normandy.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Poland.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\PortNovorossiysk.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\PortNovorossiyskBattle.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Pradesh.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Serversk-13.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Sinai.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Stalingrad.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\SunCity.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\SurroundingsOfVolokolamsk.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Sweden.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Tunisia.png",
# r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\map\Volokolamsk.png",
]
def main():
    color=[
        (255,0,0),
        (0,255,0),
        (0,0,255),
    ]
    temp=[
        r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\statesign\A.png",
        r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\statesign\B.png",
        r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\statesign\C.png",
    ]
    temp=[cv.imread(f) for f in temp]
    mask=r"C:\Program Files\WarThunder\wtequ\Opdar\asset\autofreshmap\statesign\zonemask.png"
    mask=cv.imread(mask,cv.IMREAD_GRAYSCALE)
    for f in files:
        print(f)
        m=cv.imread(f)
        for p in range(len(temp)):
            m=matchOnMap(m,temp[p],mask,color[p])
        savemat(m)


main()