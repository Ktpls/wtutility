from .autofreshmap_configmap_importref import *

blacklistedmap = [
    "air/[Ground Strike]Ruhr",
    "air/[Ground Strike]Korsun",
]

specialmapdetectors = {
    "NotWithPoint": MapDetector(
        foo='ret(not selectPoint(ptype="A"))'
    ),
}
