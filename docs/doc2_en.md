# 🎇 SuperCCM Custom Modules and Workflows

SuperCCM allows you to integrate your own algorithms into its workflow system.

## Basics: How does SuperCCM work?

SuperCCM performs tasks by integrating individual modules into a workflow.
By default, the module list is defined in:

`superccm/impl/modules.py`

```python
from superccm.core import Module

from superccm.impl.io.read import read_image
from superccm.impl.segment.segment import CornealNerveSegmenter
from superccm.impl.skeleton.skeletonize import get_skeleton
from superccm.impl.trunk.extract_trunks import extract_trunks
from superccm.impl.graph.graphify import graphify
from superccm.impl.metircs.metrics import get_metrics


class ReadModule(Module):
    Author = 'default'
    Version = '1.0.0'
    Function = read_image


class SegModule(Module):
    Author = 'default'
    Version = '1.0.0'
    Function = CornealNerveSegmenter


class SkelModule(Module):
    Author = 'default'
    Version = '1.0.0'
    Function = get_skeleton


class TrunkModule(Module):
    Author = 'default'
    Version = '1.0.0'
    Function = extract_trunks


class GraphifyModule(Module):
    Author = 'default'
    Version = '1.0.0'
    Function = graphify


class MeasureModule(Module):
    Author = 'default'
    Version = '1.0.0'
    Function = get_metrics
```

Each specific module inherits from the `Module` class.
The `Author` and `Version` attributes define the author and version information.
The core functionality is specified in the `Function` attribute, which can take either of the following:

1. A callable function
2. A class implementing the `__call__` method (but not an instance)

The default workflow is defined in:

`superccm/default.py`

```python
from superccm.core import WorkFlow
from superccm.impl.modules import (
    ReadModule, SegModule, SkelModule, TrunkModule, GraphifyModule, MeasureModule
)


class DefaultWorkFlow(WorkFlow):
    """ Default Workflow of SuperCCM for HRT III-RCM Corneal confocal microscopy image"""
    Author = 'Official'
    Version = '1.0.0'
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
        graph = self.grfy_module(image, skeleton)
        graph, trunks = self.trunk_module(graph)
        self.graph = graph
        metrics = self.meas_module(graph, binary, trunks)
        return metrics
```

Similarly, `Author` and `Version` are defined as class attributes.
Additional class attributes are used to mount the modules.

> Note: The class names of the modules and the attribute names in the workflow do not have to match—this is just an
> example.

In the `__init__` method, these modules are instantiated, and any extra logic can be added.

The `run` method defines the input-output relationships and execution order of the modules.

If we try printing the `DefaultWorkFlow`:

```python
from superccm import DefaultWorkFlow

wf = DefaultWorkFlow()
print(wf)
```

Output:

```text
<DefaultWorkFlow> Author: [Official] Version = 1.0.0 Doc: " Default Workflow of SuperCCM for HRT III-RCM Corneal confocal microscopy image"
 - <ReadModule> Author: [default] Version = 1.0.0
 - <SegModule> Author: [default] Version = 1.0.0
 - <SkelModule> Author: [default] Version = 1.0.0
 - <TrunkModule> Author: [default] Version = 1.0.0
 - <GraphifyModule> Author: [default] Version = 1.0.0
 - <MeasureModule> Author: [default] Version = 1.0.0
```

---

## Example 1: Improving the Binarization Method

Suppose you’ve developed a new binarization algorithm or model for CCM images and want to integrate it into SuperCCM.

You can wrap your algorithm as a function `sota_ccm_segment`:

```python
import numpy as np


def sota_ccm_segment(image: np.ndarray) -> np.ndarray:
    pass
```

Or as a class `SotaCcmSegmenter`:

```python
import numpy as np


class SotaCcmSegmenter:
    def __init__(self):
        self.model = 'load/your/model/checkpoint'

    def seg(self, image: np.ndarray) -> np.ndarray:
        pass
```

There are three ways to integrate this into SuperCCM:

### 1. Monkey Patching

```python
from superccm import DefaultWorkFlow

DefaultWorkFlow.SegModule.Function = sota_ccm_segment
# DefaultWorkFlow.SegModule.Function = SotaCcmSegmenter
wf = DefaultWorkFlow()
rst = wf.run('test.jpg')
```

### 2. Define a New Module

Then apply a monkey patch.

```python
from superccm import Module, DefaultWorkFlow


class MySegModule(Module):
    Author = 'You'
    Version = '1.0.0'
    Function = sota_ccm_segment
    # Function = SotaCcmSegmenter


DefaultWorkFlow.SegModule = MySegModule
```

If you print `DefaultWorkFlow` now:

```text
...
 - <MySegModule> Author: [You] Version = 1.0.0
...
```

### 3. Define a New Workflow

Inherit from the `WorkFlow` abstract class.

```python
from superccm.core import WorkFlow
from superccm.impl.modules import (
    ReadModule, SkelModule, TrunkModule, GraphifyModule, MeasureModule
)
from yourscript import MySegModule


class MyWorkFlow(WorkFlow):
    """ This is my workflow :) """
    Author = 'Me'
    Version = '999.999.999'
    ReadModule = ReadModule
    SegModule = MySegModule  # Your new module goes here
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
        graph = self.grfy_module(image, skeleton)
        graph, trunks = self.trunk_module(graph)
        self.graph = graph
        metrics = self.meas_module(graph, binary, trunks)
        return metrics
```

---

## Example 2: Adding a Preprocessing Module

Suppose you’ve developed a new preprocessing algorithm that improves the quality of CCM images and enhances subsequent
analysis.

You wrap your algorithm as a function `ccm_preprocess`:

```python
import numpy as np


def ccm_preprocess(image: np.ndarray) -> np.ndarray:
    pass
```

Define a new module:

```python
from superccm import Module


class MyPrepModule(Module):
    Author = 'Who?'
    Version = '1.0.0'
    Function = ccm_preprocess
```

Define a workflow:

```python
from superccm.core import WorkFlow
from superccm.impl.modules import (
    ReadModule, SegModule, SkelModule, TrunkModule, GraphifyModule, MeasureModule
)

from yourscript import MyPrepModule


class MyWorkFlow(WorkFlow):
    """ This is my workflow :) """
    Author = 'Who?'
    Version = '123.456.789'
    ReadModule = ReadModule
    PrepModule = MyPrepModule
    SegModule = SegModule
    SkelModule = SkelModule
    TrunkModule = TrunkModule
    GraphifyModule = GraphifyModule
    MeasureModule = MeasureModule

    def __init__(self):
        self.read_module = self.ReadModule()
        self.prep_module = self.PrepModule()  # Here
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
        graph = self.grfy_module(image, skeleton)
        graph, trunks = self.trunk_module(graph)
        self.graph = graph
        metrics = self.meas_module(graph, binary, trunks)
        return metrics
```

