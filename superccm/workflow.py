import aiccm

from .morphology import NerveImage
from .graph import NerveGraph
from .metrics import get_metrics


class SuperCCM:
    def __init__(self):
        self.nerve_image = None
        self.nerve_graph = NerveGraph
        self.metrics = {}

    def analysis(self, image, **kwargs):
        self.nerve_image = NerveImage(image)
        self.nerve_graph = NerveGraph(self.nerve_image)
        # self.nerve_graph.draw()
        self.metrics = get_metrics(self.nerve_image, self.nerve_graph)
        return self.metrics

    def __call__(self, image, **kwargs):
        return self.analysis(image, **kwargs)
