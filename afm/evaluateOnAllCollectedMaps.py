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
    clzName = make_filename_safe(str(clz))
    index = fileClassIndex[clzName] = fileClassIndex.get(clzName, 0) + 1
    if clz is None:
        fileNewPath = os.path.join(classifyResultRoot, f"{clzName}_{index:03d}.png")
        subprocess.run(f"copy {x} {fileNewPath}", shell=True, stdout=subprocess.PIPE)
    prog.update(i)
print("done")
print(ReprObject(fileClassIndex))
