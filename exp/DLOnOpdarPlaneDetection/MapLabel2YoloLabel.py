#%%
from utilref import *
from nntracker_common import labeldataset

#%%
train_data = labeldataset().init(
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\selallenhed.zip",
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\sel.xlsx",
    32768, 'zip', 'all')

#%%
standardSize = [100, 100]
S = 7


def get_AABB(binary_image):
    """
    This function takes a binary value image as input and outputs the AABB of the object in the image which is indicated by its pixel value=255.
    """
    # find the indices of non-zero elements in the binary image
    non_zero_indices = np.nonzero(binary_image)
    if non_zero_indices[0].size == 0:
        return 0, 0, 0, 0

    # get the minimum and maximum x and y coordinates of the non-zero elements
    min_x = np.min(non_zero_indices[1])
    min_y = np.min(non_zero_indices[0])
    max_x = np.max(non_zero_indices[1])
    max_y = np.max(non_zero_indices[0])

    # return the AABB
    return (min_x, min_y, max_x, max_y)


def get_centers(binary_image):
    """
    This function takes a binary value image as input and outputs the center of all 255 pixels in the image.
    """
    # find the indices of non-zero elements in the binary image
    non_zero_indices = np.nonzero(binary_image)
    if non_zero_indices[0].size == 0:
        return 0, 0

    # get the x and y coordinates of the non-zero elements
    x_coords = non_zero_indices[1]
    y_coords = non_zero_indices[0]

    # calculate the center of all 255 pixels
    center_x = np.mean(x_coords)
    center_y = np.mean(y_coords)

    # return the center
    return (int(center_x), int(center_y))


def get_grid(x, y):
    """
    This function takes in the x and y coordinates of a point in [0,1]x[0,1] space and the number of blocks S to split the space into.
    It returns the index of the block that the point lies in.
    """
    # calculate the size of each block
    block_size = 1 / S

    # calculate the x and y indices of the block that the point lies in
    x_index = int(x // block_size)
    y_index = int(y // block_size)

    # return the block index
    ret = np.zeros([S, S], np.int32)
    ret[y_index, x_index] = 1
    return ret


lines = []
for i in range(train_data.rawlength()):
    binary_image = train_data.rawgetitem(i)[1]
    binary_image = cv.resize(binary_image, standardSize)
    name = train_data.getname(i)
    AABB = get_AABB(binary_image)
    responser = get_centers(binary_image)
    lines.append(tuple(itertools.chain([name], AABB, responser)))

import openpyxl
# write AABBs to excel file using openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "AABBs"
ws.append(["Name", "Min X", "Min Y", "Max X", "Max Y", "Center X", "Center Y"])
for ln in lines:
    ws.append(ln)
wb.save(
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\AABBs.xlsx"
)
