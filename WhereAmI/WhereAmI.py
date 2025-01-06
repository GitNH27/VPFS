import sys
from RefTags import refTags
import VPFS

import cv2
import time
import os
# NOTE: pupil_apriltags seems to be broken on Python 3.12, so this needs to be run with <3.12
from pupil_apriltags import Detector

import utils

# Camera settings for Desktop mode
camera_id = 0
camera_width = 1600
camera_height = 900
# Intrinsics used in detection
cam_fx = 950
cam_fy = 950
cam_cx = 800
cam_cy = 455
camera_intrinsics = (cam_fx, cam_fy, cam_cx, cam_cy)

detector = Detector(
    nthreads=4,
    quad_decimate=1,
    quad_sigma=0.1,
    decode_sharpening=1
)

# GStreamer pipeline to work with Jetson
pipeline = ' ! '.join([
    "v4l2src device=/dev/video0",
    "video/x-raw, fomat=YUYV, width=1600, height=896, framerate=15/2",
    "videoconvert",
    "video/x-raw, format=(string)BGR",
    "appsink drop=true sync=false"
    ])

# Run with jetson CLI opt for jetson use, otherwise runs desktop mode
jetson = "jetson" in sys.argv

if jetson:
    # Configure camera for best results
    os.system("v4l2-ctl -d /dev/video0 -c focus_auto=0")
    os.system("v4l2-ctl -d /dev/video0 -c focus_absolute=0")
    # Readback current settings
    os.system("v4l2-ctl -d /dev/video0 -C focus_auto")
    os.system("v4l2-ctl -d /dev/video0 -C focus_absolute")
    cam = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
else:
    cam = cv2.VideoCapture(camera_id) # this is the magic!

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

frameWidth = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(frameWidth, 'x', frameHeight)

font = cv2.FONT_HERSHEY_PLAIN
def show_tags(img, detections):
    for tag in detections:
        img = cv2.putText(img, str(tag.tag_id), (int(tag.center[0]), int(tag.center[1])), font, 3, (0, 0, 255), 2, cv2.LINE_AA)
        img = cv2.rectangle(img, (int(tag.corners[0][0]), int(tag.corners[0][1])), (int(tag.corners[2][0]), int(tag.corners[2][1])), (0, 0, 255), 2)
    return img

def computeCameraPos(detections):
    camPos = (999, 999, 999)
    for det in detections:
        if det.tag_id in refTags:
            refPos = refTags[det.tag_id]
            tagPos = (det.pose_t[0][0], det.pose_t[1][0], det.pose_t[2][0])
            camPos = (refPos[0]-tagPos[0], refPos[1]-tagPos[1], refPos[2]-tagPos[2])
    return camPos

if not cam.isOpened():
    print("Cannot open camera")
    exit()

lastTime = time.time()
while True:
    # Capture the frame
    ret, frame = cam.read()

    if not ret:
        print("Failed to receive frame, exiting")
        break

    # Sharpen the image
    # strength = 1.75
    # blurred = cv2.GaussianBlur(frame, (0, 0), 1)
    # frame = cv2.addWeighted(frame, 1.0 + strength, blurred, -strength, 0)

    # Process the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect tags
    detections = detector.detect(gray, True, camera_intrinsics, 0.1)
    frame = show_tags(frame, detections)
    cameraPos = utils.computeCameraPos(detections)
    # Check that there was good reference tag detection
    tagPoses = []
    if cameraPos is not None:
        tagPoses = utils.computeTagPoses(detections, cameraPos)
        # Send updates to VPFS
        VPFS.send_update(tagPoses)

    # Compute FPS
    frameTime = time.time() - lastTime
    fps = 1/frameTime
    lastTime = time.time()

    # Add info block
    cv2.putText(frame, f"{frameWidth}x{frameHeight} @ {fps:.2f} fps", (0,frameHeight - 10), font, 3, (255, 255, 255), 2, cv2.LINE_AA)
    #cv2.putText(frame, f"X{cameraPos[0]:.2f} Y{cameraPos[1]:.2f} Z{cameraPos[2]:.2f}", (0, frameHeight-200), font, 3, (255, 0, 255), 2, cv2.LINE_AA)
    
    i = -100
    for tag in tagPoses:
        cv2.putText(frame, f"{tag}: X{tagPoses[tag][0]:.2f} Y{tagPoses[tag][1]:.2f} Z{tagPoses[tag][2]:.2f}", (0, frameHeight + i), font, 3, (255, 0, 255), 2, cv2.LINE_AA)
        i -= 50

    cv2.imshow('frame', frame)

    cv2.waitKey(1)

cam.release()
cv2.destroyAllWindows()
