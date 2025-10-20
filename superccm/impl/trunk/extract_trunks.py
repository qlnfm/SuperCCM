import os
import cv2
import numpy as np
import networkx as nx
from itertools import combinations

from superccm.impl.metircs.utils import graph_to_skeleton
from superccm.impl.trunk.ep_path import shortest_path
from superccm.impl.trunk.eval_path import analyze_curve_sharpness_windowed
from superccm.impl.utils.tools import get_canvas

CCM_IMAGE_SHAPE = (384, 384)


def multigraph_to_graph(G: nx.MultiGraph, weight_func) -> nx.Graph:
    """ Convert the multi-graph (MultiGraph) to a single graph while retaining the edges with the optimal weights. """
    H = nx.Graph()

    for u, v, k, d in G.edges(keys=True, data=True):
        w = weight_func(u, v, k, d)
        obj = d['obj']

        if not H.has_edge(u, v):
            H.add_edge(u, v, obj=obj)
        else:
            existing_obj = H[u][v]['obj']
            existing_w = getattr(existing_obj, 'intensity_mean', float('inf'))
            if w > existing_w:
                H[u][v]['obj'] = obj

    # Copy node attributes
    H.add_nodes_from((n, {'obj': d['obj']}) for n, d in G.nodes(data=True))
    return H


def nodes_to_edges(nodes):
    """ Node sequence to edge sequence """
    return list(zip(nodes[:-1], nodes[1:]))


def nodes_to_canvas(G: nx.Graph, nodes):
    """ Draw the path nodes as Canvas """
    canvas = get_canvas()
    for u, v in nodes_to_edges(nodes):
        canvas += G[u][v]['obj'].canvas
    for n in nodes:
        canvas += G.nodes[n]['obj'].canvas
    return canvas


def get_ep_pairs(graph: nx.Graph, img_shape):
    """ Obtain possible endpoint pairs (excluding boundary endpoints) """
    h, w = img_shape
    thresh = (h + w) / 20
    component_map = {n: idx for idx, comp in enumerate(nx.connected_components(graph)) for n in comp}

    eps = [(n, d['obj']) for n, d in graph.nodes(data=True) if d['obj'].type == 'End']
    eps_edge = []
    for n, obj in eps:
        x, y = obj.centroid
        distances = [x, y, w - x, h - y]
        ds = {f'd{i}' for i, d in enumerate(distances) if d <= thresh}
        if ds:
            eps_edge.append((n, obj, ds))

    ep_pairs = []
    for ep1, ep2 in combinations(eps_edge, 2):
        n1, obj1, ds1 = ep1
        n2, obj2, ds2 = ep2
        same_side = bool(ds1 & ds2) and (len(ds1 | ds2) < 3)
        if not same_side and component_map[n1] == component_map[n2]:
            ep_pairs.append(((n1, obj1), (n2, obj2)))
    return ep_pairs


def get_paths(graph, ep_pairs):
    """ Generate a list of paths for the endpoint pairs """
    path_list = []
    for (n1, obj1), (n2, obj2) in ep_pairs:
        x1, y1 = map(int, obj1.centroid)
        x2, y2 = map(int, obj2.centroid)

        for i, nodes in enumerate(nx.shortest_simple_paths(graph, n1, n2, weight=lambda u, v, d: d['obj'].length)):
            skeleton_p = nodes_to_canvas(graph, nodes)
            edges = nodes_to_edges(nodes)
            intensities = np.array([graph[u][v]['obj'].intensity_mean for u, v in edges])
            lengths = np.array([max(50, graph[u][v]['obj'].length) for u, v in edges])

            mean = np.mean(intensities)
            median = np.median(intensities)
            avg = np.average(intensities, weights=lengths)
            variance = np.average((intensities - avg) ** 2, weights=lengths)
            diff = intensities - avg
            max_diff = np.max(diff)

            path = shortest_path(skeleton_p, (y1, x1), (y2, x2))
            angles = analyze_curve_sharpness_windowed(path, half_window_size=15)
            max_angle = max(angles)

            if max_angle > 90:
                break

            path_list.append((path, (max_angle, variance, max_diff, mean, median), set(nodes)))
            if i >= 1:
                break  # Limit to only the first two paths/限制只取前两个路径
    return path_list


def sort_key(item):
    """ Path sorting """
    max_angle, variance, max_diff, mean, median = item[1]
    return max_angle ** (1 + min(variance, 0.01) * 20) * (1 - median)


def get_trunks(paths, skeleton):
    canvas_list = sorted(paths, key=sort_key)

    canvas_all = get_canvas(1)
    nodes_records = set()

    for path, stats, nodes in canvas_list:
        xs, ys = zip(*path)
        canvas = get_canvas(1)
        canvas[xs, ys] = skeleton[xs, ys]

        if not nodes & nodes_records:
            nodes_records.update(nodes)
            canvas_all += canvas
        nodes_records.update(nodes)

    return canvas_all


def extract_trunks(graph: nx.MultiGraph) -> tuple[nx.MultiGraph, np.ndarray]:
    graph_: nx.MultiGraph = graph.copy()
    graph_nm = multigraph_to_graph(graph, lambda u, v, k, d: d['obj'].intensity_mean)
    ep_pairs = get_ep_pairs(graph_nm, CCM_IMAGE_SHAPE)
    paths = get_paths(graph_nm, ep_pairs)
    trunk_canvas = get_trunks(paths, graph_to_skeleton(graph_))
    for _, _, _, data in graph_.edges(keys=True, data=True):
        edge_obj = data['obj']
        if np.any(cv2.bitwise_and(edge_obj.canvas, trunk_canvas)):
            edge_obj.is_trunk = True
    return graph_, trunk_canvas
