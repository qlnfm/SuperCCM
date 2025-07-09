import numpy as np
from typing import Literal
from .constant import SHAPE

CANVAS_CHANNEL = Literal[1, 3]


def get_canvas(channel: CANVAS_CHANNEL = 1):
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
