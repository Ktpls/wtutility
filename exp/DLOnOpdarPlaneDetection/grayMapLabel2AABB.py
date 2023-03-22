
#%%
from utilref import *
from nntracker_common import labeldataset

#%%
train_data = labeldataset().init(
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\selallenhed.zip",
    r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\sel.xlsx",
    32768, 'zip')

#%%
def get_AABB(binary_image):
    """
    This function takes a binary value image as input and output the AABB of object in image which is indicated with its pixel value=255
    """
    # find the indices of non-zero elements in the binary image
    non_zero_indices = np.nonzero(binary_image)
    if non_zero_indices[0].size==0:
        return 0,0,0,0

    
    # get the minimum and maximum x and y coordinates of the non-zero elements
    min_x = np.min(non_zero_indices[1])
    min_y = np.min(non_zero_indices[0])
    max_x = np.max(non_zero_indices[1])
    max_y = np.max(non_zero_indices[0])

    # return the AABB
    return (min_x, min_y, max_x, max_y)

#%%
AABBs = []
for i in range(train_data.rawlength()):
    binary_image = train_data.rawgetitem(i)[1]
    name=train_data.getname(i)
    AABB = get_AABB(binary_image)
    AABBs.append(tuple(itertools.chain([name],AABB)))

#%%
import openpyxl
# write AABBs to excel file using openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "AABBs"
ws.append(["Name", "Min X", "Min Y", "Max X", "Max Y"])
for AABB in AABBs:
    ws.append(AABB)
wb.save(r"C:\file\code\wtutility\exp\DLOnOpdarPlaneDetection\dataset\selallenhed\AABBs.xlsx")