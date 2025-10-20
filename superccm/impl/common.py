import numpy as np
from typing import Literal


def get_canvas(channel: Literal[1, 3] = 1, shape: tuple[int, int] = (384, 384)):
    """
    Get an image that is all zeros and use it as the canvas.
    :param channel: The number of channels, take 1 or 3
    :param shape: The shape of canvas, default is (384, 384)
    :return: The canvas
    """
    match channel:
        case 1:
            return np.zeros(shape, dtype='uint8')
        case 3:
            return np.zeros((*shape, 3), dtype='uint8')
