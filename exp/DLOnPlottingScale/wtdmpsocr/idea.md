use H5Ui4MarkingCharLocation to mark where plotting scales start
use output above to train nn locator
use locator to give start point on other samples, and cut char
use tesseract to auto label output above
correct auto labeled chars by hand
use output above to train nn chardetector
use chardetector to classify chars in plotting scale screenshot
and output this