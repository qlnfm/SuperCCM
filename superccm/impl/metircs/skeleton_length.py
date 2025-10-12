import cv2
import numpy as np


def get_skeleton_length(skeleton: np.ndarray) -> float:
    contours, _ = cv2.findContours(skeleton, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    length = 0
    for c in contours:
        length += cv2.arcLength(c, True) / 2
    return length
