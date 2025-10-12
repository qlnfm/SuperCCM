from superccm.core import Module

from superccm.impl.io.read import read_image
from superccm.impl.segment.segment import CornealNerveSegmenter
from superccm.impl.skeleton.skeletonize import get_skeleton
from superccm.impl.graph.graphify import graphify
from superccm.impl.metircs.metrics import get_metrics


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
