
import numpy as np
import cv2 as cv
def compare_images_by_mse(a, b):
    """
    Compare two input images a and b by pixel using mean squared error (MSE).
    Return the result.
    """
    a=cv.imread(a)[:,:,0].astype(np.float32)/255
    b=cv.imread(b)[:,:,0].astype(np.float32)/255
    mse = np.sum((a - b) ** 2)
    return mse


# We can use nested loops to compare each pair of images in the input list
# If the mean squared error between two images is below a certain threshold, we can consider them duplicates and remove one of them from the list

def deduplicate_images(images, threshold):
    """
    Compare images in input list and deduplicate them based on mean squared error (MSE) threshold.
    Return the deduplicated list of images.
    """
    deduplicated_images = []
    for i in range(len(images)):
        is_duplicate = False
        for j in range(i+1, len(images)):
            mse = compare_images_by_mse(images[i], images[j])
            if mse <= threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            deduplicated_images.append(images[i])
    return deduplicated_images

import os
src=r"D:\File\code\prog\wtutility\exp\DLOnPlottingScale\dataset\charDataset\labeled"
dst=r"D:\File\code\prog\wtutility\exp\DLOnPlottingScale\dataset\charDataset\dedued"
i=0
while(i<=10):
    try:
        os.makedirs(os.path.join(dst,f'{i}'))
    except:
        pass
    i+=1
for root,dirs,files in os.walk(src):
    files=[os.path.join(root,f'{f}') for f in files]
    dedued=deduplicate_images(files,5)
    deduedDst=[d.replace(src,dst) for d in dedued]
    for s,d in zip(dedued,deduedDst):
        print(f'{s} to {d}')
        os.system(f'copy "{s}" "{d}"')