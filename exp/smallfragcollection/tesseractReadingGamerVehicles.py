import sys

sys.path.append(r".")
from utilitypack import *
import pytesseract.pytesseract as pytesseract
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img_path = r"C:\Users\Kita\Desktop\tessertest.png"
img = cv.imread(img_path)
text = pytesseract.image_to_string(img)
print(text)

'''
u got 5 and S mixed together.
just transform them all to 5 or S
'''