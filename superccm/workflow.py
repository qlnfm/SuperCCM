from collections.abc import Sequence
from typing import Any, Callable
from .modules import (
    BaseModule, ReadImageModule, SegmentModule, SkeletonizeModule, GraphifyModule, MetricsModule
)

default_modules = [
    ReadImageModule,
    SegmentModule,
    SkeletonizeModule,
    GraphifyModule,
    MetricsModule,
]


def default_workflow(img) -> dict[str, tuple[Any]]:
    return {
        'read': (img, 'gray'),
        'segment': ('[Data]raw_image',),
        'skeletonize': ('[Data]binary_image',),
        'graphify': ('[Data]raw_image', '[Data]binary_image', '[Data]skeleton_image'),
        'metrics': ('[Data]nerve_graph', ),
    }


class SuperCCM:
    def __init__(
            self,
            modules: Sequence[type[BaseModule]] | None = None,
            workflow: Callable = None
    ):
        modules = modules if modules is not None else default_modules
        self.modules: list[BaseModule] = [m() for m in modules]
        self.workflow = workflow if workflow is not None else default_workflow
        self.data = {}

    def run(self, *args, **kwargs):
        import time
        time_records = {}
        output = None
        workflow = self.workflow(*args, **kwargs)
        for module in self.modules:
            module_name, output_name = module.name, module.output_name
            inputs = workflow[module_name]
            inputs = tuple(self.data[x[6:]] if isinstance(x, str) and x.startswith('[Data]') else x for x in inputs)

            start = time.perf_counter()
            output = module(*inputs)
            time_records[module_name] = time.perf_counter() - start

            if output_name is not None:
                self.data[output_name] = output
        # print(time_records)
        return output

    @property
    def graph(self):
        return self.data.get('nerve_graph')

