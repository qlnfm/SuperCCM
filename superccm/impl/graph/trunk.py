import networkx as nx
from superccm.impl.utils.curvature import get_curvature

# 主干寻找参数
ALPHA = 0.5  # 曲率权重
BETA = 0.5  # 强度权重


class EdgeStack:
    def __init__(self, graph: nx.MultiGraph):
        self.graph = graph
        stack = [(u, v, k) for u, v, k in self.graph.edges(keys=True)]
        stack = list(sorted(
            stack,
            key=lambda x: len(graph.get_edge_data(*x)['obj'].coords),
            reverse=True
        ))
        stack = list(sorted(
            stack,
            key=lambda x: graph.get_edge_data(*x)['obj'].intensity_median,
            reverse=True
        ))
        self.stack = stack

    @classmethod
    def uvk_equal(cls, uvk1: tuple[int, int, int], uvk2: tuple[int, int, int]):
        u1, v1, k1 = uvk1
        u2, v2, k2 = uvk2
        return ((u1 == u2 and v1 == v2) or (u1 == v2 and v1 == u2)) and (k1 == k2)

    def get_obj(self, uvk: tuple[int, int, int]):
        return self.graph.get_edge_data(*uvk)['obj']

    def __getitem__(self, item):
        return self.stack[item]

    def __contains__(self, item: tuple[int, int, int]):
        u, v, k = item
        return (u, v, k) in self.stack or (v, u, k) in self.stack

    def index(self, item: tuple[int, int, int]):
        if item not in self.stack:
            return None
        u, v, k = item
        try:
            return self.stack.index((u, v, k))
        except ValueError:
            return self.stack.index((v, u, k))

    def remove(self, item: tuple[int, int, int]):
        if item not in self.stack:
            return
        index = self.index(item)
        self.stack.pop(index)

    def pop(self, index: int):
        return self.stack.pop(index)

    def __str__(self):
        return str(self.stack)

    def __bool__(self):
        return bool(self.stack)

    def __len__(self):
        return len(self.stack)


def cal_edge_diff(
        graph: nx.MultiGraph,
        cur_edge_uvk: tuple[int, int, int],
        node_idx: int,
        next_edge_uvk: tuple[int, int, int],
) -> float:
    """计算两条相邻边的差异度，用于主干生长决策"""
    cur_edge_obj = graph.edges[cur_edge_uvk]['obj']
    next_edge_obj = graph.edges[next_edge_uvk]['obj']

    kappa_diff = get_curvature(graph, node_idx, cur_edge_uvk, next_edge_uvk)
    # 使用中位数强度差异作为衡量标准，更稳健
    intensity_diff = abs(cur_edge_obj.intensity_median - next_edge_obj.intensity_median)
    diff = ALPHA * kappa_diff + BETA * intensity_diff
    return diff


def assign_trunks(graph: nx.MultiGraph) -> nx.MultiGraph:
    g: nx.MultiGraph = graph.copy()
    connected_comps = list(nx.connected_components(g))
    for comp in connected_comps:
        subgraph = g.subgraph(comp).copy()
        subgraph: nx.MultiGraph

        node_stack, global_node_record = [], set()
        all_edges_stack = EdgeStack(subgraph)

        while all_edges_stack:
            fail = False
            seed_edge_uvk = cur_edge_uvk = all_edges_stack.pop(0)

            # 检查此seed边是否合法
            u, v, _ = seed_edge_uvk
            if u in global_node_record and v in global_node_record:
                continue
            if u in global_node_record or v in global_node_record:
                fail = True

            node_stack.append(u)
            node_stack.append(v)
            global_node_record.add(u)
            global_node_record.add(v)
            trunk_edges = [cur_edge_uvk]

            while node_stack:
                node_idx = node_stack.pop()
                node_obj = subgraph.nodes(data=True)[node_idx]['obj']
                # 如果达到了端点，从seed edge的另一侧开始
                if node_obj.type == 'End':
                    cur_edge_uvk = seed_edge_uvk
                    continue

                # 如果没有，找到这个点的所有邻边
                edges_ngb = list(subgraph.edges(node_idx, keys=True))
                min_diff = float('inf')
                next_edge_uvk = None
                for uvk_ in edges_ngb:
                    # 防止和本身比较
                    if EdgeStack.uvk_equal(cur_edge_uvk, uvk_):
                        continue
                    diff = cal_edge_diff(subgraph, cur_edge_uvk, node_idx, uvk_)
                    if diff < min_diff:
                        min_diff = diff
                        next_edge_uvk = uvk_

                all_edges_stack.remove(next_edge_uvk)
                # 检查此邻边是否合法
                u, v, _ = next_edge_uvk
                if u in global_node_record and v in global_node_record:
                    fail = True
                    # 换另一边
                    cur_edge_uvk = seed_edge_uvk
                    continue

                trunk_edges.append(next_edge_uvk)
                cur_edge_obj = all_edges_stack.get_obj(next_edge_uvk)
                # cur_edge_obj.color = 'red'
                cur_edge_uvk = next_edge_uvk
                u, v, k = cur_edge_uvk
                if u not in global_node_record:
                    node_stack.append(u)
                    global_node_record.add(u)
                if v not in global_node_record:
                    node_stack.append(v)
                    global_node_record.add(v)

            if not fail:
                for edge in trunk_edges:
                    edge_obj = all_edges_stack.get_obj(edge)
                    edge_obj.color = 'red'
                    edge_obj.is_trunk = True
    return g


def get_trunk_groups(G: nx.MultiGraph):
    """
    返回所有 trunk 边的连通分量，每个分量包含：
      {
          "nodes": [node1, node2, ...],
          "edges": [(u, v, k), ...],
          "node_objs": [obj1, obj2, ...],  # 对应节点的 obj（如果有）
          "edge_objs": [obj1, obj2, ...],  # 对应边的 obj
      }
    """
    # 1. 找出 trunk 边
    trunk_edges = [
        (u, v, k)
        for u, v, k, d in G.edges(keys=True, data=True)
        if hasattr(d.get("obj", None), "is_trunk") and d["obj"].is_trunk
    ]

    # 2. 构建 trunk 子图
    trunk_subgraph = G.edge_subgraph(trunk_edges).copy()

    # 3. 找出连通分量
    components = nx.connected_components(trunk_subgraph)

    # 4. 收集每个分量的节点、边及 obj
    groups = []
    for nodes in components:
        sub = trunk_subgraph.subgraph(nodes)
        edges = list(sub.edges(keys=True))

        group = {
            "nodes": list(nodes),
            "edges": edges,
            "node_objs": [G.nodes[n].get("obj") for n in nodes if "obj" in G.nodes[n]],
            "edge_objs": [
                G[u][v][k]["obj"]
                for u, v, k in edges
                if "obj" in G[u][v][k]
            ],
        }
        groups.append(group)

    return groups
