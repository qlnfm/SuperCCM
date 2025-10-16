from superccm.core import WorkFlow
from superccm.impl.modules import (
    ReadModule, SegModule, SkelModule, TrunkModule, GraphifyModule, MeasureModule
)


class DefaultWorkFlow(WorkFlow):
    """ Default Workflow of SuperCCM Ver 0.5.0 """
    Author = 'Official'
    Version = '0.5.0'
    ReadModule = ReadModule
    SegModule = SegModule
    SkelModule = SkelModule
    TrunkModule = TrunkModule
    GraphifyModule = GraphifyModule
    MeasureModule = MeasureModule

    def __init__(self):
        self.read_module = self.ReadModule()
        self.seg_module = self.SegModule()
        self.skel_module = self.SkelModule()
        self.trunk_module = self.TrunkModule()
        self.grfy_module = self.GraphifyModule()
        self.meas_module = self.MeasureModule()
        self.image = None
        self.graph = None

    def run(self, image_or_path):
        image = self.read_module(image_or_path)
        self.image = image
        binary = self.seg_module(image)
        skeleton = self.skel_module(binary)
        trunk = self.trunk_module(image, skeleton)
        graph = self.grfy_module(image, skeleton, trunk)
        self.graph = graph
        metrics = self.meas_module(graph, binary)
        return metrics
