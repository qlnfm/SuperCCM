from skimage.morphology import skeletonize
import numpy as np
import cv2


def _skeletonize_255(image: np.ndarray) -> np.ndarray:
    image = image > 0
    skeleton = skeletonize(image)
    skeleton = skeleton.astype('uint8')
    skeleton = skeleton * 255
    return skeleton


def get_skeleton(image: np.ndarray, x: int = 1) -> np.ndarray:
    skeleton = _skeletonize_255(image)
    # skeleton_closed = cv2.morphologyEx(skeleton, cv2.MORPH_CLOSE, (3, 3))
    # skeleton = _skeletonize_255(skeleton_closed)

    # 设置边缘 x 像素为 0
    skeleton[:x, :] = 0          # 上边
    skeleton[-x:, :] = 0         # 下边
    skeleton[:, :x] = 0          # 左边
    skeleton[:, -x:] = 0         # 右边

    return skeleton

