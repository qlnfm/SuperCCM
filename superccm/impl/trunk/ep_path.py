import numpy as np
import networkx as nx
from scipy.ndimage import convolve, generate_binary_structure
from itertools import combinations


def find_endpoints(skeleton):
    struct = generate_binary_structure(2, 2)
    neighbor_sum = convolve(skeleton, struct, mode='constant', cval=0)
    neighbors = neighbor_sum - skeleton
    endpoints = np.argwhere((skeleton == 1) & (neighbors == 1))
    return [tuple(ep) for ep in endpoints]


def build_graph(skeleton):
    G = nx.Graph()
    rows, cols = skeleton.shape
    for i in range(rows):
        for j in range(cols):
            if skeleton[i, j] == 1:
                G.add_node((i, j))
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for i in range(rows):
        for j in range(cols):
            if skeleton[i, j] == 1:
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols and skeleton[ni, nj] == 1:
                        G.add_edge((i, j), (ni, nj))
    return G


def get_edge_endpoints(endpoints, skeleton, x):
    rows, cols = skeleton.shape
    edge_eps = []
    for ep in endpoints:
        r, c = ep
        dist_top = r
        dist_bottom = rows - 1 - r
        dist_left = c
        dist_right = cols - 1 - c
        if min(dist_top, dist_bottom, dist_left, dist_right) <= x:
            edge_eps.append(ep)
    return edge_eps


def get_sides(ep, skeleton, x):
    rows, cols = skeleton.shape
    r, c = ep
    sides = set()
    if r <= x:
        sides.add('top')
    if r >= rows - 1 - x:
        sides.add('bottom')
    if c <= x:
        sides.add('left')
    if c >= cols - 1 - x:
        sides.add('right')
    return sides


def same_side(ep1, ep2, skeleton, x):
    sides1 = get_sides(ep1, skeleton, x)
    sides2 = get_sides(ep2, skeleton, x)
    return bool(sides1 & sides2)  # 有交集则同一侧


def get_paths(skeleton, side_x=10):
    x = side_x
    skeleton = skeleton > 0
    skeleton = skeleton.astype('uint8')

    endpoints = find_endpoints(skeleton)
    edge_endpoints = get_edge_endpoints(endpoints, skeleton, x)
    G = build_graph(skeleton)

    # 获取连通组件映射
    component_map = {}
    for idx, component in enumerate(nx.connected_components(G)):
        for node in component:
            component_map[node] = idx

    all_shortest_paths = {}
    for ep1, ep2 in combinations(edge_endpoints, 2):
        if not same_side(ep1, ep2, skeleton, x) and component_map.get(ep1) == component_map.get(ep2):
            try:
                path = nx.shortest_path(G, ep1, ep2)
                all_shortest_paths[(ep1, ep2)] = path
            except nx.NetworkXNoPath:
                pass

    return all_shortest_paths
