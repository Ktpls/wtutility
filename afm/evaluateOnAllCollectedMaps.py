from utilref import *
import afm.autofreshmap_implementation as afmi
import superstream as ss
import json


class AllMapShapeConfigMimic:
    def __init__(self):
        root = r"asset\autofreshmap\map\\"
        maps = AllFileIn(root)
        maps = [m.replace(root, "") for m in maps]
        pngPattern = regex.compile(r"\.png", regex.IGNORECASE)
        maps = [regex.sub(pngPattern, "", m) for m in maps]
        self.whitelistedmap = maps


aa = afmi.AfmAsset(AllMapShapeConfigMimic())
stateDetector, mapDetector = aa.stateDetector, aa.mapDetector


def TryClassifyOneMap(filepath):
    mapImg = cv.imread(filepath).astype(np.float32) / 255
    mapImgProced = afmi.MapImgComparator.imagepreprocess(mapImg)
    for n, d in mapDetector.items():
        if d.detect(mapImg, mapImgProced):
            return n
    return None 


map2classifyRoot = r"asset\collection\afm\map"
classifyResultRoot = r"output"
fileClassIndex = {}
maps = AllFileIn(map2classifyRoot)
prog = Progress(len(maps))
for i, x in enumerate(maps):
    clz = TryClassifyOneMap(x)
    clzName = "Unknown" if clz is None else (clz.replace("\\", "_"))
    if clzName not in fileClassIndex:
        fileClassIndex[clzName] = 0
    else:
        fileClassIndex[clzName] += 1
    index = fileClassIndex[clzName]
    fileNewPath = os.path.join(classifyResultRoot, f"{clzName}_{index:03d}.png")
    if clz is None:
        os.system(f"copy {x} {fileNewPath}")
    prog.update(i)
print("done")
print(json.dumps(fileClassIndex, indent=4))
