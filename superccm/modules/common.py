import numpy as np
from typing import Literal

# Image shape
SHAPE = (384, 384)


def get_canvas(channel: Literal[1, 3] = 1):
    """
    Get an image that is all zeros and use it as the canvas.
    :param channel: The number of channels, take 1 or 3
    :return: The canvas
    """
    match channel:
        case 1:
            return np.zeros(SHAPE, dtype='uint8')
        case 3:
            return np.zeros((*SHAPE, 3), dtype='uint8')
