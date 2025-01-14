import numpy as np
from numpy.typing import *
from typing import Dict, Tuple
import RefTags

# See PhotonVision CMP 2024 talk, starting around 20:00

# Camera is at it's own origin, so transform is just identity

# World-To-Tag transformation matrices
# Rotations are all zero to make life simple
refTags = RefTags.refTags

def det_to_transform_mat(detection) -> ArrayLike:
    """
    Convert detection information into homogenous transformation matrix form
    :param detection: Tag detection information
    :return: Homogenous transformation matrix
    """
    trans = detection.pose_t
    rot = detection.pose_R
    
    # Combine to obtain homogeneous transformation matrix
    mat = np.concatenate((rot, trans), axis=1)
    mat = np.concatenate((mat, [[0,0,0,1]]), axis=0)
    return mat

def compute_camera_pos(detections) -> ArrayLike or None:
    """
    Compute the camera's position in the map coordinate system based on detected reference tags
    :param detections: List of all tag detections
    :return: Map-to-camera-space transformation matrix, or None if no reference tags found
    """
    map_to_cam = None
    
    for det in detections:
        if det.tag_id in refTags:
            cam_to_tag = det_to_transform_mat(det)
            map_to_cam = np.matmul(refTags[det.tag_id].mat, np.linalg.inv(cam_to_tag))
    
    return map_to_cam

def compute_tag_poses(detections, cam_pos: ArrayLike) -> Dict[int, Tuple[int, int, int]]:
    """
    Compute the map-space poses of tags based on the camera's position in map-space
    :param detections: List of all tag detections
    :param cam_pos: Map-to-camera-space transformation matrix, from compute_camera_pos
    :return: Dictionary with tag (X,Y,Z), indexed by tag ID
    """
    tag_poses = {}
    for det in detections:
        tag_pose = det_to_transform_mat(det)
        tag_pose = np.matmul(cam_pos, tag_pose)
        tag_poses[det.tag_id] = (
                tag_pose[0][3],
                tag_pose[1][3],
                tag_pose[2][3]
                )
    return tag_poses
