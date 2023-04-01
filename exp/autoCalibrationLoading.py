from utilref import *


def recon():
    # Load input image
    input_image = cv.imread(r'.\output\testofwtdmp\src.png')

    # Convert input image to HSV color space
    hsv_image = cv.cvtColor(input_image, cv.COLOR_BGR2HSV).astype(np.float32)

    # Define lower and upper bounds for red color in HSV color space
    # shift hue up by range, move parts over 360 back to hue-360
    # then filter [0,2*range]
    huerange = 20
    hsv_image += np.array([[hsv2opencv8bithsv((huerange, 0, 0))]])
    huemax = hsv2opencv8bithsv((360, 0, 0))[0]
    hsv_image[hsv_image[:, :, 0] > huemax, 0] -= huemax
    lower_red = hsv2opencv8bithsv((0, 40, 40))
    upper_red = hsv2opencv8bithsv((2 * huerange, 100, 100))
    red_mask = cv.inRange(hsv_image, lower_red, upper_red) / 255
    #  apply ui mask here
    uimask = cv.imread(r".\asset\opdar\UIMASK.png")[:, :, 0].astype(
        np.float32) / 255
    red_mask = red_mask * uimask
    savematflt(red_mask)

    # use distribution to find crosshair
    distOnX = red_mask.sum(axis=0)
    distOnY = red_mask.sum(axis=1)
    crosshair = [np.argmax(distOnY), np.argmax(distOnX)]
    crosshairSafeThresh = 500
    if distOnX[crosshair[1]] < crosshairSafeThresh or distOnY[
            crosshair[0]] < crosshairSafeThresh:
        return (
            'AC_BAD_CRHR, maybe go try switch night mode or just not in snipping'
        )

    # search graduation around vertical crosshair line, again use distribution
    gridSearchWidth = 10
    gridSearchRange = np.array(
        [crosshair[1] - gridSearchWidth, crosshair[1] + gridSearchWidth])

    #[AllowedRange[0],AllowedRange[1]), left closed right open
    def validateCoor(AllowedRange, coor):
        if coor < AllowedRange[0]:
            coor = AllowedRange[0]
        if coor >= AllowedRange[1]:
            coor = AllowedRange[1] - 1
        return coor

    for i in range(len(gridSearchRange)):
        gridSearchRange[i] = validateCoor([0, red_mask.shape[1]],
                                          gridSearchRange[i])
    distOnY_Grid = (red_mask[:, gridSearchRange[0]:gridSearchRange[1]]).sum(
        axis=1)
    line = distOnY_Grid > 10 if gridSearchWidth >= 10 else distOnY_Grid > 0.5 * gridSearchWidth

    # suppress line detection around horizontal crosshair line
    forbidenWidthAroundCrosshair = 5
    forbidenRangeAroundCrosshair = [
        crosshair[0] - forbidenWidthAroundCrosshair,
        crosshair[0] + forbidenWidthAroundCrosshair
    ]
    for i in range(len(gridSearchRange)):
        forbidenRangeAroundCrosshair[i] = validateCoor(
            [0, red_mask.shape[0]], forbidenRangeAroundCrosshair[i])
    line[forbidenRangeAroundCrosshair[0]:
         forbidenRangeAroundCrosshair[1]] = False

    #degenerate wide line occupying multiple rows into one
    line = line.astype(np.float32)
    degenWindow = 3
    i = 0
    while i < len(line) - degenWindow:
        windowSum = line[i:i + degenWindow].sum()
        if windowSum > 1:
            center = (np.arange(i, i + degenWindow) *
                      line[i:i + degenWindow]).sum() / windowSum
            line[i:i + degenWindow] = 0
            line[int(center)] = 1
        i += 1
    line = line > 0.5
    #rebuild
    rebuildMap = np.zeros_like(red_mask)
    rebuildMap[crosshair[0], :] = 1
    rebuildMap[:, crosshair[1]] = 1
    rebuildMap[line, gridSearchRange[0]:gridSearchRange[1]] = 1
    savematflt(rebuildMap)

    linepos = np.where(line)[0]
    

    def regression(x, y):
        m = len(x)
        x_bar = np.mean(x)
        w = (np.sum(
            (x - x_bar) * y)) / (np.sum(x**2) - (1 / m) * (np.sum(x))**2)
        b = np.mean(y - w * x)
        return w, b

    y = np.arange(1, 1 + len(linepos)) * 100
    w, b = regression(linepos, y)
    
    return crosshair[0]*w+b


print(recon())