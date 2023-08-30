from utilref import *
from wtdmpsocr import getmodel, tsize, tsizep1, typeElse, device


def move_image_to_center(image):
    # Find AABB
    non_zero_pixels = np.nonzero(image)
    min_x, max_x = np.min(non_zero_pixels[1]), np.max(non_zero_pixels[1])
    min_y, max_y = np.min(non_zero_pixels[0]), np.max(non_zero_pixels[0])

    # Calculate center point
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_x_img = image.shape[1] / 2
    center_y_img = image.shape[0] / 2

    # Calculate translation vector
    translation_x = center_x_img - center_x
    translation_y = center_y_img - center_y

    # Create new blank image
    new_image = np.zeros_like(image)

    # Move pixels to center using warp affine
    M = np.float32([[1, 0, translation_x], [0, 1, translation_y]])
    new_image = cv.warpAffine(image, M, (image.shape[1], image.shape[0]))
    new_image = (new_image > 255//2).astype(np.int32)*255

    translation_vector = [
        translation_x,
        translation_y,
    ]  # replace with your actual translation vector
    magnitude = np.sqrt(sum([x**2 for x in translation_vector]))
    return new_image, magnitude


path = rf"C:\prog\wtutility\exp\DLOnPlottingScale\dataset\charDataset\labeled"
translations = []
for t in range(tsize):
    rootoft = rf"{path}\{t}"
    if os.path.exists(rootoft):
        piclist = AllFileIn(rootoft)
        for p in piclist:
            image = cv.imread(p, cv.IMREAD_GRAYSCALE)
            image, tr = move_image_to_center(image)
            cv.imwrite(p, image)
            translations.append(tr)

# Plotting the distribution of translations
plt.hist(translations, bins=20)
plt.xlabel("Translation")
plt.ylabel("Frequency")
plt.title("Distribution of Translations")
plt.show()
