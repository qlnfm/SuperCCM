# 🎇 SuperCCM Custom Modules & Workflows

SuperCCM allows you to integrate your own algorithms into its workflows.

## Basics: How does SuperCCM work?

SuperCCM executes tasks by integrating each **Module** into a **Workflow**.
By default, the module list is defined in:

`superccm/impl/modules.py`

```python
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
```

Each specific module inherits from the `Module` class.
The `Author` and `Version` class attributes define metadata.
The `Function` class attribute defines the actual functionality, which accepts two types of inputs:

1. A **function** (callable object)
2. A **class that implements `__call__`** (not an instance)

The default workflow is defined in:

`superccm/default.py`

```python
from .core import WorkFlow
from .impl.modules import (
    ReadModule, SegModule, SkelModule, GraphifyModule, MeasureModule
)


class DefaultWorkFlow(WorkFlow):
    """ Default Workflow of SuperCCM Ver 0.3.0 """
    Author = 'Official'
    Version = '0.3.0'
    ReadModule = ReadModule
    SegModule = SegModule
    SkelModule = SkelModule
    GraphifyModule = GraphifyModule
    MeasureModule = MeasureModule

    def __init__(self):
        self.read_module = self.ReadModule()
        self.seg_module = self.SegModule()
        self.skel_module = self.SkelModule()
        self.grfy_module = self.GraphifyModule()
        self.meas_module = self.MeasureModule()
        self.graph = None

    def run(self, image_input):
        image = self.read_module(image_input)
        binary = self.seg_module(image)
        skeleton = self.skel_module(binary)
        graph = self.grfy_module(image, binary, skeleton)
        self.graph = graph
        metrics = self.meas_module(graph)
        return metrics
```

Similarly, `Author` and `Version` are defined as class attributes.
Additional class attributes are used to mount `Module`s.

> Note: The class names of modules and the workflow’s class attributes do not need to match. This is just a convention in the default workflow.

In the `__init__` method, modules are instantiated and additional custom logic can be implemented.

In the `run` method, the specific input/output and execution order of each module are defined.

If we print the `DefaultWorkFlow`:

```python
from superccm import DefaultWorkFlow

wf = DefaultWorkFlow()
print(wf)
```

```text
<DefaultWorkFlow> Author: [Official] Version = 0.3.0 Doc: " Default Workflow of SuperCCM Ver 0.3.0 "
 - <ReadModule> Author: [default] Version = 0.1.0
 - <SegModule> Author: [default] Version = 0.1.0
 - <SkelModule> Author: [default] Version = 0.1.0
 - <GraphifyModule> Author: [default] Version = 0.1.0
 - <MeasureModule> Author: [default] Version = 0.1.0
```

---

## Example 1: Improving the Binarization Method

Suppose you developed a novel CCM image binarization algorithm or model and want to integrate it into SuperCCM.

You can wrap it as a function:

```python
import numpy as np

def sota_ccm_segment(image: np.ndarray) -> np.ndarray:
    pass
```

Or as a class:

```python
import numpy as np

class SotaCcmSegmenter:
    def __init__(self):
        self.model = 'load/your/model/checkpoint'

    def seg(self, image: np.ndarray) -> np.ndarray:
        pass
```

You now have three ways to integrate it into SuperCCM:

### 1. Monkey Patching

```python
from superccm import DefaultWorkFlow

DefaultWorkFlow.SegModule.Function = sota_ccm_segment
# DefaultWorkFlow.SegModule.Function = SotaCcmSegmenter
wf = DefaultWorkFlow()
rst = wf.run('test.jpg')
```

### 2. Define a New Module

And then apply monkey patching.

```python
from superccm import Module, DefaultWorkFlow

class MySegModule(Module):
    Author = 'You'
    Version = '1.0.0'
    Function = sota_ccm_segment
    # Function = SotaCcmSegmenter

DefaultWorkFlow.SegModule = MySegModule
```

Now if we print `DefaultWorkFlow`:

```text
<DefaultWorkFlow> Author: [Official] Version = 0.3.0 Doc: " Default Workflow of SuperCCM Ver 0.3.0 "
 - <ReadModule> Author: [default] Version = 0.1.0
 - <MySegModule> Author: [You] Version = 1.0.0
 - <SkelModule> Author: [default] Version = 0.1.0
 - <GraphifyModule> Author: [default] Version = 0.1.0
 - <MeasureModule> Author: [default] Version = 0.1.0
```

### 3. Define a New Workflow

By inheriting the abstract class `WorkFlow`:

```python
from superccm import WorkFlow
from .impl.modules import (
    ReadModule, SegModule, SkelModule, GraphifyModule, MeasureModule
)

class MyWorkFlow(WorkFlow):
    """ This is my workflow :) """
    Author = 'Me'
    Version = '999.999.999'
    ReadModule = ReadModule
    SegModule = MySegModule
    SkelModule = SkelModule
    GraphifyModule = GraphifyModule
    MeasureModule = MeasureModule

    def __init__(self):
        self.read_module = self.ReadModule()
        self.seg_module = self.SegModule()
        self.skel_module = self.SkelModule()
        self.grfy_module = self.GraphifyModule()
        self.meas_module = self.MeasureModule()
        self.graph = None

    def run(self, image_input):
        image = self.read_module(image_input)
        binary = self.seg_module(image)
        skeleton = self.skel_module(binary)
        graph = self.grfy_module(image, binary, skeleton)
        self.graph = graph
        metrics = self.meas_module(graph)
        return metrics
```

---

## Example 2: Adding a Preprocessing Module

Suppose you developed a novel CCM image preprocessing algorithm that improves image quality and enhances subsequent analysis.

You wrap it as a function:

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
from superccm import WorkFlow
from .impl.modules import (
    ReadModule, SegModule, SkelModule, GraphifyModule, MeasureModule
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
    GraphifyModule = GraphifyModule
    MeasureModule = MeasureModule

    def __init__(self):
        self.read_module = self.ReadModule()
        self.prep_module = self.PrepModule()  # Here
        self.seg_module = self.SegModule()
        self.skel_module = self.SkelModule()
        self.grfy_module = self.GraphifyModule()
        self.meas_module = self.MeasureModule()
        self.graph = None

    def run(self, image_input):
        image = self.read_module(image_input)
        image_prep = self.prep_module(image)
        binary = self.seg_module(image_prep)
        skeleton = self.skel_module(binary)
        graph = self.grfy_module(image_prep, binary, skeleton)
        self.graph = graph
        metrics = self.meas_module(graph)
        return metrics
```
