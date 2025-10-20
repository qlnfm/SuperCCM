import numpy as np
import networkx as nx
from scipy.ndimage import binary_dilation
from superccm.impl.utils.tools import get_canvas


def check_connectivity(mask1: np.ndarray, mask2: np.ndarray) -> str:
    """
    Determine the connectivity relationship between two regions:
    Return value:
    '8-connected' -> The two regions are 8-connected (including 4-connected cases)
    '4-connected' -> Only 4-connected (not 8-connected)
    'disconnected' -> Not connected
    """
    mask1 = mask1 > 0
    mask2 = mask2 > 0
    selem_8 = np.ones((3, 3), dtype=bool)
    selem_4 = np.array([[0, 1, 0],
                        [1, 1, 1],
                        [0, 1, 0]], dtype=bool)

    if np.any(binary_dilation(mask1, structure=selem_8) & mask2):
        return '8-connected'

    elif np.any(binary_dilation(mask1, structure=selem_4) & mask2):
        return '4-connected'

    else:
        return 'disconnected'


def graph_to_skeleton(graph: nx.MultiGraph) -> np.ndarray:
    canvas = get_canvas(1)
    for u, v, k, data in graph.edges(keys=True, data=True):
        edge_obj = data['obj']
        canvas = canvas + edge_obj.canvas

    for idx, data in graph.nodes(data=True):
        node_obj = data['obj']
        canvas = canvas + node_obj.canvas

    return canvas
