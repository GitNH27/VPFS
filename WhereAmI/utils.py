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

def detToTransformMat(detection):
    trans = detection.pose_t
    rot = detection.pose_R
    
    # Combine to obtain homogenious transformation matrix
    mat = np.concatenate((rot, trans), axis=1)
    mat = np.concatenate((mat, [[0,0,0,1]]), axis=0)
    return mat

def computeCameraPos(detections):
    mapToCam = np.array([
        [1,0,0,999],
        [0,1,0,999],
        [0,0,1,999],
        [0,0,0,1]
        ])
    
    for det in detections:
        if det.tag_id in refTags:
            camToTag = detToTransformMat(det)
            mapToCam = np.matmul(refTags[det.tag_id], np.linalg.inv(camToTag))
    
    return mapToCam

def computeTagPoses(detections, camPos):
    tagPoses = {}
    for det in detections:
        tagPose = detToTransformMat(det)
        tagPose = np.matmul(camPos, tagPose)
        tagPoses[det.tag_id] = (
                tagPose[0][3],
                tagPose[1][3],
                tagPose[2][3]
                )
    return tagPoses
