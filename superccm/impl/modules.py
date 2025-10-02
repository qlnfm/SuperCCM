from ..core import Module

from .io.read import read_image
from .segment.segment import CornealNerveSegmenter
from .skeleton.skeletonize import get_skeleton
from .topology.graphify import graphify
from .metircs.metrics import get_metrics


class ReadModule(Module):
    Author = 'default'
    Version = '0.1.0'
    Function = read_image


class SegModule(Module):
    Author = 'default'
    Version = '0.1.0'
    Function = CornealNerveSegmenter


class SkelModule(Module):
    Author = 'default'
    Version = '0.1.0'
    Function = get_skeleton


class GraphifyModule(Module):
    Author = 'default'
    Version = '0.1.0'
    Function = graphify


class MeasureModule(Module):
    Author = 'default'
    Version = '0.1.0'
    Function = get_metrics
