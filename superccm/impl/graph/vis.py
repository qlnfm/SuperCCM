import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import cv2
from matplotlib.path import Path
import matplotlib.patches as patches
from superccm.impl.utils.tools import get_canvas


def vis_graph(g: nx.MultiGraph):
    """ Visualize NetworkX MultiGraph, supporting smooth Bezier curve display for multiple edges."""
    fig, ax = plt.subplots(figsize=(8, 8))

    # ---- Draw nodes ----
    node_positions = {}
    for n, data in g.nodes(data=True):
        obj = data.get("obj")
        if not hasattr(obj, "centroid"):
            continue

        x, y = obj.centroid
        node_positions[n] = (x, y)

        color = 'blue' if getattr(obj, 'type', None) == 'End' else 'green'
        ax.scatter(x, y, color=color, s=35, zorder=5)
        ax.text(x, y, str(n), fontsize=9, color='black',
                ha='center', va='center', zorder=6)

    # ---- Grouped edges (based on node pairs) ----
    edge_groups = {}
    for u, v, key, data in g.edges(keys=True, data=True):
        pair = tuple(sorted([u, v]))
        edge_groups.setdefault(pair, []).append((key, data))

    # ---- Draw edges ----
    for (u, v), edges in edge_groups.items():
        u_obj, v_obj = g.nodes[u].get("obj"), g.nodes[v].get("obj")
        if not (hasattr(u_obj, "centroid") and hasattr(v_obj, "centroid")):
            continue

        x1, y1 = u_obj.centroid
        x2, y2 = v_obj.centroid
        dx, dy = x2 - x1, y2 - y1
        length = np.hypot(dx, dy)
        if length == 0:
            continue

        n_edges = len(edges)
        perp_x, perp_y = -dy / length, dx / length

        for i, (_, data) in enumerate(edges):
            edge_obj = data.get('obj')
            color = 'red' if getattr(edge_obj, 'is_trunk', False) else 'black'
            lw = getattr(edge_obj, 'intensity_mean', 0.5) * 2

            if n_edges == 1:
                # Single edge: Straight line
                ax.plot([x1, x2], [y1, y2], '-', alpha=0.7, zorder=2,
                        linewidth=lw, color=color)
            else:
                # Multiple edges: Bezier curve
                offset = (length * 0.3) * (2 * i / (n_edges - 1) - 1)
                cp1 = (x1 + dx * 0.3 + perp_x * offset * 0.7,
                       y1 + dy * 0.3 + perp_y * offset * 0.7)
                cp2 = (x1 + dx * 0.7 + perp_x * offset * 0.7,
                       y1 + dy * 0.7 + perp_y * offset * 0.7)

                path = Path(
                    [(x1, y1), cp1, cp2, (x2, y2)],
                    [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
                )
                ax.add_patch(patches.PathPatch(
                    path, facecolor='none', edgecolor=color,
                    lw=lw, alpha=0.7, zorder=2
                ))

    ax.set_aspect('equal', 'box')
    ax.invert_yaxis()
    plt.show()


def vis_ACCM(g: nx.MultiGraph, background: np.ndarray | None = None):
    """ Presented in an output style similar to ACCMetrics. """
    background = get_canvas(3) if background is None else background.copy()
    if background.ndim == 2:
        background = cv2.cvtColor(background, cv2.COLOR_GRAY2BGR)

    # ---- Draw edges ----
    for _, _, _, data in g.edges(keys=True, data=True):
        edge_obj = data['obj']
        color = (0, 0, 255) if getattr(edge_obj, 'is_trunk', False) else (255, 0, 0)
        background[edge_obj.canvas > 0] = color

    # ---- Draw nodes ----
    for _, data in g.nodes(data=True):
        node_obj = data['obj']
        if getattr(node_obj, 'type', None) == 'End':
            continue

        color = (0, 255, 0)
        x, y = map(int, node_obj.centroid)
        cv2.rectangle(background, (x - 1, y - 1), (x + 1, y + 1), color, -1)
        background[node_obj.canvas > 0] = color

    return background
