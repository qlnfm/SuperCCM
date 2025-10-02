import cv2
from typing import Literal


class SkeletonComponent:
    def __init__(self, component_type: Literal['node', 'edge'], index: int, coords: list[tuple[int, int]]):
        self.type = component_type
        self.node_type: Literal['end', 'branch'] | None = None
        self.edge_type: Literal['main', 'side'] | None = None
        self.index = index
        self.coords = coords.copy()
        self.bone = None
        self.body = None

        self.neighbors = []
        self.weights = []

        self.color = None

        self._centroid = None
        self._length = None
        self._width = None

    def __repr__(self):
        return f'SkeletonComponent("{self.type}", {self.index}, {self.coords})'

    def __str__(self):
        match self.type:
            case 'node':
                desc = f'[Node](index: {self.index}, centroid: {self.centroid})'
            case 'edge':
                desc = f'[Edge](index: {self.index}, length: {self.length:.2f}, weight: {self.width:.2f}'
                if self.edge_type is not None:
                    desc += f', type: {self.edge_type}'
                desc += ')'
            case _:
                desc = 'Error'
        return desc

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
            contours, _ = cv2.findContours(self.bone, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                length += cv2.arcLength(c, True) / 2
            self._length = length
        return self._length

    @property
    def width(self):
        if self._width is None:
            self._width = (sum(self.weights) / len(self.weights)) if self.weights else 0
        return self._width
