import numpy as np
import networkx as nx
from scipy.ndimage import binary_dilation
from superccm.impl.utils.tools import get_canvas


def check_connectivity(mask1: np.ndarray, mask2: np.ndarray) -> str:
    """
    判断两个区域之间的连通性关系：
    返回值：
        '8-connected'  -> 两区域8连通（包含4连通情况）
        '4-connected'  -> 仅4连通（非8连通）
        'disconnected' -> 不连通
    """
    if mask1.shape != mask2.shape:
        raise ValueError("mask1 和 mask2 必须形状相同")

    # 转为布尔掩膜
    mask1 = mask1 > 0
    mask2 = mask2 > 0
    # 8连通结构元素（3x3全1）
    selem_8 = np.ones((3, 3), dtype=bool)
    # 4连通结构元素（十字形）
    selem_4 = np.array([[0, 1, 0],
                        [1, 1, 1],
                        [0, 1, 0]], dtype=bool)

    # 检查8连通（包括4连通情况）
    if np.any(binary_dilation(mask1, structure=selem_8) & mask2):
        return '8-connected'

    # 检查4连通（排除8连通后）
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
