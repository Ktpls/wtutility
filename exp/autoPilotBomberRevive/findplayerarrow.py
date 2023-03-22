import cv2
import numpy as np

def find_arrow(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            if (theta > np.pi/4 and theta < 3*np.pi/4) or (theta > 5*np.pi/4 and theta < 7*np.pi/4):
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                return (x1, y1), (x2, y2)
    return None

