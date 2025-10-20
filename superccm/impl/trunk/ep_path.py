from collections import deque
import numpy as np


def shortest_path(img, start, goal, connectivity=8):
    """
    Find shortest path between start and goal traveling only through non-zero pixels (e.g. 255).
    Uses BFS (unweighted shortest path on grid). Returns list of (r,c) inclusive from start to goal,
    or None if no path exists.

    Parameters
    ----------
    img : array-like (H, W)
        Binary image with values 0 (background) or non-zero (foreground). Will be interpreted as boolean.
    start : tuple (r, c)
        Start coordinate (row, col).
    goal : tuple (r, c)
        Goal coordinate (row, col).
    connectivity : {4, 8}
        Pixel adjacency. 4 for NSEW, 8 includes diagonals.
    """
    arr = np.asarray(img)
    if arr.ndim != 2:
        raise ValueError("img must be 2D")
    H, W = arr.shape
    sr, sc = start
    gr, gc = goal
    # bounds check
    if not (0 <= sr < H and 0 <= sc < W):
        raise ValueError("start out of bounds")
    if not (0 <= gr < H and 0 <= gc < W):
        raise ValueError("goal out of bounds")
    # convert to boolean mask
    mask = arr != 0
    if not mask[sr, sc]:
        return None  # start on background
    if not mask[gr, gc]:
        return None  # goal on background
    if (sr, sc) == (gr, gc):
        return [(sr, sc)]
    # flattened indexing for speed
    N = H * W
    start_idx = sr * W + sc
    goal_idx = gr * W + gc
    visited = np.zeros(N, dtype=np.bool_)
    parent = np.full(N, -1, dtype=np.int32)  # store parent index for path reconstruction
    dq = deque()
    dq.append(start_idx)
    visited[start_idx] = True
    parent[start_idx] = -2  # sentinel for start
    # neighbor offsets (in r,c) to iterate
    if connectivity == 4:
        neigh = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    elif connectivity == 8:
        neigh = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    else:
        raise ValueError("connectivity must be 4 or 8")
    # BFS loop
    while dq:
        idx = dq.popleft()
        r = idx // W
        c = idx - r * W  # faster than divmod
        # iterate neighbors
        for dr, dc in neigh:
            nr = r + dr
            nc = c + dc
            if nr < 0 or nr >= H or nc < 0 or nc >= W:
                continue
            nidx = nr * W + nc
            if visited[nidx]:
                continue
            if not mask[nr, nc]:
                continue
            visited[nidx] = True
            parent[nidx] = idx
            if nidx == goal_idx:
                # reconstruct path
                path = []
                cur = nidx
                while cur != -2:
                    cr = cur // W
                    cc = cur - cr * W
                    path.append((cr, cc))
                    cur = parent[cur]
                path.reverse()
                return path
            dq.append(nidx)
    # no path found
    return None
