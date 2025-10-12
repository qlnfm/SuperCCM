import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import cv2
from matplotlib.path import Path
import matplotlib.patches as patches

from superccm.impl.utils.tools import get_canvas


def vis_graph(g: nx.MultiGraph):
    fig, ax = plt.subplots(figsize=(8, 8))

    # ---- 绘制节点 ----
    node_positions = {}
    for n, data in g.nodes(data=True):
        if hasattr(data.get("obj"), "centroid"):
            x, y = data["obj"].centroid
            type_ = data['obj'].type
            node_positions[n] = (x, y)
            color = 'blue' if type_ == 'End' else 'green'
            ax.scatter(x, y, color=color, s=35, zorder=5)
            ax.text(x, y, str(n), fontsize=9, color='black', ha='center', va='center', zorder=6)

    # ---- 绘制边 ----
    edge_groups = {}

    # 分组边：按节点对分组
    for u, v, key, data in g.edges(keys=True, data=True):
        pair = tuple(sorted([u, v]))
        if pair not in edge_groups:
            edge_groups[pair] = []
        edge_groups[pair].append((key, data))

    # 为每对节点绘制多条边
    for pair, edges in edge_groups.items():
        u, v = pair
        u_obj = g.nodes[u].get("obj")
        v_obj = g.nodes[v].get("obj")

        if not (hasattr(u_obj, "centroid") and hasattr(v_obj, "centroid")):
            continue

        x1, y1 = u_obj.centroid
        x2, y2 = v_obj.centroid

        # 计算边的数量
        n_edges = len(edges)

        for i, (key, data) in enumerate(edges):
            # 计算曲线控制点
            if n_edges == 1:
                # 单条边：使用直线
                color = 'red' if data.get('obj').is_trunk else 'black'

                ax.plot([x1, x2], [y1, y2], '-', alpha=0.7, zorder=2,
                        linewidth=data.get('obj').intensity_mean * 2 if hasattr(data.get('obj'),
                                                                                'intensity_mean') else 1,
                        color=color)
            else:
                # 多条边：使用贝塞尔曲线
                # 计算垂直方向
                dx, dy = x2 - x1, y2 - y1
                length = np.sqrt(dx ** 2 + dy ** 2)

                if length == 0:
                    continue

                # 垂直向量（归一化）
                perp_x, perp_y = -dy / length, dx / length

                # 计算曲线偏移量（根据边的数量调整）
                max_offset = length * 0.3  # 最大偏移量为边长的30%
                offset = max_offset * (2 * i / (n_edges - 1) - 1)  # 从 -max_offset 到 +max_offset

                # 贝塞尔曲线控制点
                control_dist = length * 0.3  # 控制点距离
                cp1_x = x1 + dx * 0.3 + perp_x * offset * 0.7
                cp1_y = y1 + dy * 0.3 + perp_y * offset * 0.7
                cp2_x = x1 + dx * 0.7 + perp_x * offset * 0.7
                cp2_y = y1 + dy * 0.7 + perp_y * offset * 0.7

                # 创建贝塞尔曲线路径
                vertices = [(x1, y1),
                            (cp1_x, cp1_y),
                            (cp2_x, cp2_y),
                            (x2, y2)]
                codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]

                path = Path(vertices, codes)
                color = 'red' if data.get('obj').is_trunk else 'black'
                patch = patches.PathPatch(path,
                                          facecolor='none',  # 确保填充为无
                                          edgecolor=color,
                                          lw=data.get('obj').intensity_mean * 2 if hasattr(data.get('obj'),
                                                                                           'intensity_mean') else 1,
                                          alpha=0.7,
                                          zorder=2,
                                          fill=False)  # 确保不填充
                ax.add_patch(patch)

    ax.set_aspect('equal', 'box')
    ax.set_title("MultiGraph with Curved Edges")
    ax.invert_yaxis()
    plt.show()
    plt.close()


def vis_ACCM(g: nx.MultiGraph, background: np.ndarray | None = None):
    if background is None:
        background = get_canvas(3)
    if background.ndim == 2:
        background = cv2.cvtColor(background, cv2.COLOR_GRAY2BGR)

    for u, v, k, data in g.edges(keys=True, data=True):
        edge_obj = data['obj']
        color = (0, 0, 255) if edge_obj.is_trunk else (255, 0, 0)
        background[edge_obj.canvas > 0] = color
    for idx_node, data in g.nodes(data=True):
        node_obj = data['obj']
        if node_obj.type == 'End':
            continue
        color = (0, 255, 0)
        x, y = tuple(int(n) for n in node_obj.centroid)
        cv2.rectangle(background, (x - 1, y - 1), (x + 1, y + 1), color, -1)
        background[node_obj.canvas > 0] = color

    return background
