import aiccm
import numpy as np
from scipy.ndimage import label
from .constant import *

# 常量
STRUCTURE_4 = np.array([[0, 1, 0],
                        [1, 1, 1],
                        [0, 1, 0]])

STRUCTURE_8 = np.array([[1, 1, 1],
                        [1, 1, 1],
                        [1, 1, 1]])


def split(image, split_skeleton=False):
    image = image > 0
    if not split_skeleton:
        arrays, num = label(image, structure=STRUCTURE_4)
    else:
        arrays, num = label(image, structure=STRUCTURE_8)

    segments = []
    for i in range(1, num + 1):
        component_image = np.where(arrays == i, 1, 0)
        component_image = component_image * 255
        component_image = component_image.astype('uint8')
        segments.append(component_image)

    return segments, num


def get_binary(image):
    """ Binary semantic segmentation """
    binary = aiccm.get_binary(image)
    min_area, min_edge_area = MIN_BINARY_AREA, MIN_BINARY_EDGE_AREA
    # Filter out noise
    if min_area > 0 or min_edge_area > 0:
        segments, _ = split(binary, True)

        h, w = binary.shape
        edge_margin = 3  # How many pixels away from the edge is considered close to the edge

        for segment in segments:
            ys, xs = np.nonzero(segment)
            area = len(xs)

            # Whether it is within the edge range
            near_edge = (
                np.any(xs < edge_margin) or np.any(xs >= w - edge_margin) or
                np.any(ys < edge_margin) or np.any(ys >= h - edge_margin)
            )

            threshold = min_edge_area if near_edge else min_area

            if area < threshold:
                binary[segment > 0] = 0  # Delete the areas that do not meet the area requirements

    return binary

