from utilref import *

# Load input image
input_image = cv.imread(r'.\output\testofwtdmp\src.png').astype(np.float32)

# Convert input image to HSV color space
hsv_image = cv.cvtColor(input_image, cv.COLOR_BGR2HSV)

# Define lower and upper bounds for red color in HSV color space
lower_red = hsv2opencv8bithsv(0, 50, 50)
upper_red = hsv2opencv8bithsv(10, 100, 100)

# Create a mask for red color using the lower and upper bounds
red_mask = cv.inRange(hsv_image, lower_red, upper_red)

# Apply the mask to the input image to filter out red parts
filtered_image = cv.bitwise_and(input_image, input_image, mask=red_mask)

# Display the filtered image
cv.imshow('Filtered Image', filtered_image)
cv.waitKey(0)
cv.destroyAllWindows()
