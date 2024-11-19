import numpy as np

# See PhotonVision CMP 2024 talk, starting around 20:00

# Camera is at it's own origin, so transform is just identity

# World-To-Tag transformation matrices
# Rotations are all zero to make life simple
refTags = {
    0: np.array([
        [1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]
        ])

}

def computeCameraPos(detections):
    camPos = (999, 999, 999)
    
    for det in detections:
        if det.tag_id in refTags:
            camPos = (-det.pose_t[0][0], -det.pose_t[1][0], -det.pose_t[2][0])
    
    return camPos

def computeTagPoses(detections, camPos):
    tagPoses = {}
    for det in detections:
        tagPoses[det.tag_id] = (
                camPos[0] + det.pose_t[0][0],
                camPos[1] + det.pose_t[1][0],
                camPos[2] + det.pose_t[2][0]
                )
    return tagPoses
