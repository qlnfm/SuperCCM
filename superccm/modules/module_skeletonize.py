from .base import BaseModule
from skimage.morphology import skeletonize
import numpy as np


def _get_skeleton(image):
    image = image > 0
    skeleton = skeletonize(image)
    skeleton = skeleton.astype('uint8')
    skeleton = skeleton * 255

    # 设置边缘像素为0
    skeleton[0, :] = 0
    skeleton[-1, :] = 0
    skeleton[:, 0] = 0
    skeleton[:, -1] = 0

    return skeleton


class SkeletonizeModule(BaseModule):
    """
    A module used for skeletonize a binary CCM images,
    This module is expected to accept input in the format of (384, 384), with values of 0 or 255,
    and the output format is (384, 384), with values of 0 or 255.
    """

    def __init__(self):
        super().__init__()
        self.name = 'skeletonize'
        self.output_name = 'skeleton_image'

    def __call__(self, *args, **kwargs) -> np.ndarray:
        if not args:
            raise ValueError("An input is required.")
        return _get_skeleton(*args, **kwargs)
