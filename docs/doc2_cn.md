# 🎇SuperCCM 自定义模块与工作流

SuperCCM允许将你的算法集成到它的工作流中。

## 基础知识: SuperCCM是如何工作的?

SuperCCM是通过将每个模块(Module)整合到工作流(Workflow)中来执行任务的。
默认情况下，模块列表为:

`superccm/impl/modules.py`

```python
from superccm.core import Module

from superccm.impl.io.read import read_image
from superccm.impl.segment.segment import CornealNerveSegmenter
from superccm.impl.skeleton.skeletonize import get_skeleton
from superccm.impl.trunk.extract_trunk import extract_trunk
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


class TrunkModule(Module):
    Author = 'default'
    Version = '0.1.0'
    Function = extract_trunk


class GraphifyModule(Module):
    Author = 'default'
    Version = '0.1.0'
    Function = graphify


class MeasureModule(Module):
    Author = 'default'
    Version = '0.1.0'
    Function = get_metrics
```

每个特定的模块继承自`Module`类，Author和Version定义了作者和版本号的信息。
具体的功能实现在Function类属性定义，它接受两种输入:

1. 函数(Callable对象)
2. 实现了__call__方法的类(并非实例)

默认工作流则为:

`superccm/default.py`

```python
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
```

同样的，在类属性处定义了Author和Version。
此外，还有额外的类属性用于挂载Module。
> 注意，模块的类名和WorkFlow的类属性不必重名，此处仅为特例。

在__init__方法中将这些Module实例化，并实现一些额外的、自定义的逻辑。

在run方法中具体定义每个Module实例的输入输出和执行顺序。

假如我们尝试打印DefaultWorkFlow:

```python
from superccm import DefaultWorkFlow

wf = DefaultWorkFlow()
print(wf)
```

```text
<DefaultWorkFlow> Author: [Official] Version = 0.5.0 Doc: " Default Workflow of SuperCCM Ver 0.5.0 "
 - <ReadModule> Author: [default] Version = 0.1.0
 - <SegModule> Author: [default] Version = 0.1.0
 - <SkelModule> Author: [default] Version = 0.1.0
 - <TrunkModule> Author: [default] Version = 0.1.0
 - <GraphifyModule> Author: [default] Version = 0.1.0
 - <MeasureModule> Author: [default] Version = 0.1.0
```

## 例子1: 改进二值化方法

假如你开发了一种新颖的CCM图像二值化算法或模型，并且想要集成到SuperCCM中。

你将此算法包装为`sota_ccm_segment`方法:

```python
import numpy as np


def sota_ccm_segment(image: np.ndarray) -> np.ndarray:
    pass
```

或者`SotaCcmSegmenter`类:

```python
import numpy as np


class SotaCcmSegmenter:
    def __init__(self):
        self.model = 'load/your/model/checkpoint'

    def seg(self, image: np.ndarray) -> np.ndarray:
        pass
```

此时，你有三种方法将其集成在SuperCCM中:

### 1. 猴子补丁(Monkey Patching)

```python
from superccm import DefaultWorkFlow

DefaultWorkFlow.SegModule.Function = sota_ccm_segment
# DefaultWorkFlow.SegModule.Function = SotaCcmSegmenter
wf = DefaultWorkFlow()
rst = wf.run('test.jpg')
```

### 2. 定义新模块

然后再打一个猴子补丁。

```python
from superccm import Module, DefaultWorkFlow

class MySegModule(Module):
    Author = 'You'
    Version = '1.0.0'
    Function = sota_ccm_segment
    # Function = SotaCcmSegmenter

DefaultWorkFlow.SegModule = MySegModule
```
此时再打印DefaultWorkFlow:
```text
...
 - <MySegModule> Author: [You] Version = 1.0.0
...
```

### 3. 定义新工作流

继承WorkFlow抽象类。
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


## 例子2: 增加一个预处理模块

假如你开发了一种新颖的CCM图像预处理算法，它可以改善CCM图像质量，并增强后续的分析效能。

你将此算法包装为`ccm_preprocess`方法:

```python
import numpy as np


def ccm_preprocess(image: np.ndarray) -> np.ndarray:
    pass
```

定义新模块:
```python
from superccm import Module

class MyPrepModule(Module):
    Author = 'Who?'
    Version = '1.0.0'
    Function = ccm_preprocess
```

定义工作流:
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

