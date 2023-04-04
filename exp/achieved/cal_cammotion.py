
import sys
from time import sleep
sys.path.append('.')
from antiairfirecontrol import *
# Read input video
cap = cv.VideoCapture(r"D:\output\wtplane.avi")
# Get frame count
n_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT)) 
# Get width and height of video stream
w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH)) 
h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
# Define the codec for output video
fourcc = cv.VideoWriter_fourcc(*'XVID')
# Set up output video
fps = 5
out = cv.VideoWriter(r"D:\output\f_marked.avi", fourcc, fps, (w, h), False)

# Read first frame
_, prev = cap.read()

# Convert frame to grayscale
prev_gray = cv.cvtColor(prev, cv.COLOR_BGR2GRAY)

def cammotion(m0,m1):
    prev_pts = cv.goodFeaturesToTrack(m0,
                                        maxCorners=100,
                                        qualityLevel=0.001,
                                        minDistance=30,
                                        blockSize=3)

    # Calculate optical flow (i.e. track feature points)
    curr_pts, status, err = cv.calcOpticalFlowPyrLK(m0, m1, prev_pts, None) 

    # Sanity check
    assert prev_pts.shape == curr_pts.shape 

    # Filter only valid points
    idx = np.where(status==1)[0]
    prev_pts = prev_pts[idx]
    curr_pts = curr_pts[idx]

    #Find transformation matrix
    #m = cv.estimateRigidTransform(prev_pts, curr_pts, fullAffine=False) #will only work with OpenCV-3 or less
    m = cv.estimateAffinePartial2D(prev_pts, curr_pts, False)[0]

    # Extract traslation
    dx = m[0,2]
    dy = m[1,2]

    return len(prev_pts),[dx,dy]

t0=time.perf_counter()
for i in range(n_frames-2):

    # Read next frame
    success, curr = cap.read() 
    if not success:
        break

    # Convert to grayscale
    curr_gray = cv.cvtColor(curr, cv.COLOR_BGR2GRAY) 
    
    ptsnum,motion=cammotion(prev_gray,curr_gray)

    # Move to next frame
    prev_gray = curr_gray

    orgpoint=np.array([w/2,h/2],np.int32)
    dstpoint=orgpoint+np.array(motion,np.int32)
    output_gray=cv.line(
        curr_gray,
        orgpoint,
        dstpoint,
        127)
    print("Frame: " + str(i) +  "/" + str(n_frames) + " -  Tracked points : " + str(ptsnum))
    out.write(output_gray)
t1=time.perf_counter()
print('time cost:',t1-t0)

out.release()