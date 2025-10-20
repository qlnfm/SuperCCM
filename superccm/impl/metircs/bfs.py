from collections import deque
import numpy as np


def find_nearest_valid_point(image, point, max_radius=5):
    from itertools import product
    x0, y0 = point
    height, width = image.shape

    for r in range(1, max_radius + 1):
        for dx, dy in product(range(-r, r + 1), repeat=2):
            x, y = x0 + dx, y0 + dy
            if 0 <= x < width and 0 <= y < height and image[y, x] == 255:
                return (x, y)
    return None


def find_shortest_path(image, start, end):
    """
    Find the shortest path in a binary image (255 = valid path, 0 = obstacle).
    Uses 8-connected BFS.

    Parameters:
        image (np.ndarray): 2D binary image (values: 0 or 255)
        start (tuple): (x, y) start point
        end (tuple): (x, y) end point

    Returns:
        list of (x, y): shortest path from start to end, or None if no path
    """
    if not isinstance(image, np.ndarray) or image.ndim != 2:
        raise ValueError("Input 'image' must be a 2D NumPy array.")

    height, width = image.shape

    def is_valid(pos):
        x, y = pos
        return (
                0 <= x < width and
                0 <= y < height and
                image[y, x] == 255
        )

    if not is_valid(start):
        start = find_nearest_valid_point(image, start)
    if not is_valid(end):
        end = find_nearest_valid_point(image, end)

    if start is None or end is None:
        return None

    directions = [  # 8-connectivity
        (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]

    queue = deque([start])
    visited = set([start])
    parent = {start: None}

    while queue:
        current = queue.popleft()

        if current == end:
            # Reconstruct path
            path = []
            while current:
                path.append(current)
                current = parent[current]
            return path[::-1]

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if is_valid(neighbor) and neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return None  # No path found
