import numpy as np
from .graph import NerveImage, NerveGraph


def graphify(image: np.ndarray, binary_image: np.ndarray, skeleton_image: np.ndarray):
    nerve_image = NerveImage(image, binary_image, skeleton_image)
    nerve_graph = NerveGraph(nerve_image)
    return nerve_graph
