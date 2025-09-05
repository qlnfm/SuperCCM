from .base import BaseModule
from .segment.seg import segment_an_ccm_image

import numpy as np
from scipy.ndimage import label

# The smallest pixel size of the binarized segmented area is used for filtering.
MIN_BINARY_AREA = 128
# The smallest pixel size of the area located at the edge of the image after binarized segmentation, used for filtering.
MIN_BINARY_EDGE_AREA = 32
# kernel
STRUCTURE_4 = np.array([[0, 1, 0],
                        [1, 1, 1],
                        [0, 1, 0]])
STRUCTURE_8 = np.array([[1, 1, 1],
                        [1, 1, 1],
                        [1, 1, 1]])


def _split(image, split_skeleton=False):
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


def _get_binary(image):
    """ Binary semantic segmentation """
    binary = segment_an_ccm_image(image)
    min_area, min_edge_area = MIN_BINARY_AREA, MIN_BINARY_EDGE_AREA
    # Filter out noise
    if min_area > 0 or min_edge_area > 0:
        segments, _ = _split(binary, True)

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


class SegmentModule(BaseModule):
    """
    A module used for binarizing CCM images,
    This module is expected to accept input in the format of (384, 384, 3),
    and the output format is (384, 384), with values of 0 or 255.
    """
    def __init__(self):
        super().__init__()
        self.name = 'segment'
        self.output_name = 'binary_image'

    def __call__(self, *args, **kwargs) -> np.ndarray:
        if not args:
            raise ValueError("An input is required.")
        return _get_binary(*args, **kwargs)


