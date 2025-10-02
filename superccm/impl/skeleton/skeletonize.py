from skimage.morphology import skeletonize
import numpy as np


def get_skeleton(image: np.ndarray) -> np.ndarray:
    image = image > 0
    skeleton = skeletonize(image)
    skeleton = skeleton.astype('uint8')
    skeleton = skeleton * 255

    # Set the edge pixels to 0
    skeleton[0, :] = 0
    skeleton[-1, :] = 0
    skeleton[:, 0] = 0
    skeleton[:, -1] = 0

    return skeleton
