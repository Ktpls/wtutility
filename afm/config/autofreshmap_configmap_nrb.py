from .autofreshmap_configmap_importref import *
whitelistedmap = [
    r"navy\JapanesePort",
]
specialmapdetectors = {
	"navy\JapanesePort":MapDetector(
        map="navy\JapanesePort",
        foo="ret(detectMapShape(thresh=0.25))",
    ),
	
}
