from superccm.core import WorkFlow
from superccm.impl.modules import (
    ReadModule, SegModule, SkelModule, TrunkModule, GraphifyModule, MeasureModule
)


class DefaultWorkFlow(WorkFlow):
    """ Default Workflow of SuperCCM for Corneal confocal microscopy image"""
    Author = 'Official'
    Version = '1.1.0'
    ReadModule = ReadModule
    SegModule = SegModule
    SkelModule = SkelModule
    TrunkModule = TrunkModule
    GraphifyModule = GraphifyModule
    MeasureModule = MeasureModule

    def __init__(self, um_per_pixel=400/384):
        self.read_module = self.ReadModule()
        self.seg_module = self.SegModule()
        self.skel_module = self.SkelModule()
        self.trunk_module = self.TrunkModule()
        self.grfy_module = self.GraphifyModule()
        self.meas_module = self.MeasureModule()
        self.image = None
        self.graph = None

        self.area = None
        self.mask = None
        self.view_pixel_ratio = um_per_pixel

    def run(self, image_or_path):
        image, mask, area = self.read_module(image_or_path)
        self.image, self.mask, self.area = image, mask, area
        binary = self.seg_module(image)
        skeleton = self.skel_module(binary, mask, self.view_pixel_ratio)
        graph = self.grfy_module(image, skeleton)
        graph, trunks = self.trunk_module(graph, mask)
        self.graph = graph
        metrics = self.meas_module(graph, binary, trunks, area, self.view_pixel_ratio)
        return metrics
