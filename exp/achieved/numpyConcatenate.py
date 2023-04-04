
import sys
sys.path.append('.')
from utility import *
base_pts_X=np.linspace(0,1,3)
base_pts_Y=np.linspace(0,1,2)
base_pts_X,base_pts_Y=np.meshgrid(base_pts_X,base_pts_Y)
base_pts_X=base_pts_X.reshape([2,3,1])
base_pts_Y=base_pts_Y.reshape([2,3,1])
base_pts=np.concatenate((base_pts_X,base_pts_Y),2)
pass