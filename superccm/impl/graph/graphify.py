import cv2
import numpy as np
import networkx as nx
from superccm.impl.utils.tools import (
    get_split_label, get_coordinates, get_8_neighbors, get_conv2d,
    get_canvas,
)
from superccm.impl.utils.histogram_matching import histogram_standardization
from superccm.impl.utils.ccm_vignetting import vignetting_correction
from superccm.impl.utils.estimate_width import estimate_width

from typing import Literal

CLASSIFY_KERNEL = np.array([
    [1, 1, 1],
    [1, 10, 1],
    [1, 1, 1]
], dtype='uint8')


class GraphComponent:
    def __init__(self, canvas_, type_: Literal['End', 'Branch', 'Edge']):
        self.canvas = canvas_.copy()
        self.coords = get_coordinates(canvas_)
        self.type = type_
        self._centroid = None
        self._length = None

    @property
    def centroid(self):
        if self._centroid is None:
            n = len(self.coords)
            x, y = zip(*self.coords)
            centroid = round(sum(x) / n, 2), round(sum(y) / n, 2)
            self._centroid = centroid
        return self._centroid

    @property
    def length(self):
        """
        The length of the line segment is 1 for horizontal or vertical connections, and sqrt(2) for diagonal connections
        """
        if self._length is None:
            if len(self.coords) == 1:
                return 1
            length = 0
            contours, _ = cv2.findContours(self.canvas, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                length += cv2.arcLength(c, True) / 2
            self._length = length
        return self._length


class GraphEdge(GraphComponent):
    def __init__(self, canvas_, type_: Literal['End', 'Branch', 'Edge'] = 'Edge'):
        super().__init__(canvas_, type_)
        self.intensity_median = None  # value in (0, 1]
        self.intensity_mean = None  # value also in (0, 1]
        self.color = 'black'
        self.is_trunk = False

    def cal_intensity(self, intensity_map):
        if self.intensity_median is None or self.intensity_mean is None:
            nonzero_pixels = intensity_map[self.canvas > 0]
            if nonzero_pixels.size == 0:
                return 0
            self.intensity_median = np.median(nonzero_pixels) / 255
            self.intensity_mean = np.mean(nonzero_pixels) / 255


def skeleton_to_graph(skeleton: np.ndarray) -> nx.MultiGraph:
    g = nx.MultiGraph()
    skeleton_cls = get_conv2d(skeleton / 255, CLASSIFY_KERNEL)

    # Convert short links to dots
    canvas_12 = get_canvas(1)
    canvas_12[skeleton_cls == 12] = 255
    for label in get_split_label(canvas_12):
        if cv2.countNonZero(label) <= 2:
            skeleton_cls[label > 0] = 13

    # Create a table to quickly query which Node a certain coordinate belongs to/创建一个表，以快速查询某个坐标属于哪个Node
    node_coords = {}

    # Add endpoint Node
    canvas_eps = get_canvas(1)
    canvas_eps[skeleton_cls == 11] = 255
    for idx, label in enumerate(get_split_label(canvas_eps)):
        node = GraphComponent(label, 'End')
        g.add_node(idx, obj=node)
        coords = get_coordinates(label)
        for coord in coords:
            node_coords[coord] = idx

    # Add branching point Node
    canvas_eps = get_canvas(1)
    canvas_eps[skeleton_cls >= 13] = 255
    nodes_num = len(g.nodes)
    for idx, label in enumerate(get_split_label(canvas_eps)):
        node = GraphComponent(label, 'Branch')
        g.add_node(idx + nodes_num, obj=node)
        coords = get_coordinates(label)
        for coord in coords:
            node_coords[coord] = idx + nodes_num

    # ADD Edge
    canvas_eps = get_canvas(1)
    canvas_eps[skeleton_cls == 12] = 255
    for idx, label in enumerate(get_split_label(canvas_eps)):
        edge_cls = get_conv2d(label / 255, CLASSIFY_KERNEL)
        edge_eps = get_coordinates(edge_cls, 11)
        node_ids = []
        for ep in edge_eps:
            ep_nbs = get_8_neighbors(*ep)
            for nb in ep_nbs:
                if nb in node_coords:
                    node_ids.append(node_coords[nb])
        assert len(node_ids) == 2
        edge = GraphEdge(label)
        g.add_edge(node_ids[0], node_ids[1], obj=edge)

    return g


def graphify(
        image: np.ndarray,
        skeleton: np.ndarray,
) -> nx.MultiGraph:
    graph = skeleton_to_graph(skeleton)
    # Assignment intensity
    image_std = histogram_standardization(image)
    image_vig = vignetting_correction(image_std)
    intensity_map = estimate_width(image_vig, skeleton)
    for _, _, _, data in graph.edges(keys=True, data=True):
        edge_obj = data['obj']
        edge_obj.cal_intensity(intensity_map)

    return graph
