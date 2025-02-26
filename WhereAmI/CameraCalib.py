import numpy as np
import cv2 as cv
import os
 
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((5*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:5].T.reshape(-1,2)
 
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
 
# GStreamer pipeline to work with Jetson
pipeline = ' ! '.join([
    "v4l2src device=/dev/video0",
    "video/x-raw, fomat=YUYV, width=1600, height=896, framerate=15/2",
    "videoconvert",
    "video/x-raw, format=(string)BGR",
    "appsink drop=true sync=false"
    ])

# Configure camera for best results
os.system("v4l2-ctl -d /dev/video0 -c focus_auto=0")
os.system("v4l2-ctl -d /dev/video0 -c focus_absolute=0")
# Readback current settings
os.system("v4l2-ctl -d /dev/video0 -C focus_auto")
os.system("v4l2-ctl -d /dev/video0 -C focus_absolute")
cam = cv.VideoCapture(pipeline, cv.CAP_GSTREAMER)


while True:
    ret, img = cam.read()
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
 
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7,5), None)
 
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
 
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
 
        # Draw and display the corners
        cv.drawChessboardCorners(img, (7,5),  corners2, ret)
        cv.imshow('img', img)
        key = cv.waitKey(500)
        if key == ord('q'):
            break
 
cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print(mtx)
print("fx:", mtx[0][0])
print("fy:", mtx[1][1])
print("cx:", mtx[0][2])
print("cy:", mtx[1][2])
