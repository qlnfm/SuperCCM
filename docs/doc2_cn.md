# 🎇SuperCCM 自定义模块与工作流

SuperCCM允许将你的算法集成到它的工作流中。
> 如果你不想亲自动手，请联系[我](jugking6688@gmail.com)[jugking6688@gmail.com]，我会在24小时内回复。

## 基础知识: SuperCCM是如何工作的?

SuperCCM是通过顺序拼接模块(module)来执行任务的，
并且通过工作流(workflow)来控制具体的参数。
默认情况下，模块列表和工作流分别为:

```python
from typing import Any
from superccm.modules import (
    ReadImageModule, SegmentModule, SkeletonizeModule, GraphifyModule, MetricsModule
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
        'metrics': ('[Data]nerve_graph',),
    }
```

举个例子，对于模块`SegmentModule`来说，它用于执行二值化图像任务:

```python
from superccm.modules.base import BaseModule


class SegmentModule(BaseModule):
    """
    A module used for binarizing CCM images,
    This module is expected to accept input in the format of (384, 384, 3),
    and the output format is (384, 384), with values of 0 or 255.
    """

    def __init__(self):
        super().__init__()
        self.name = 'segment'
        self.output_name = 'binary_image'

    def __call__(self, *args, **kwargs) -> np.ndarray:
        if not args:
            raise ValueError("An input is required.")
        return _get_binary(*args, **kwargs)
```

- `SegmentModule`继承于`BaseModule`，这是一个抽象基类，
  要求模块有一个`__call__`方法，并且定义好`self.name`和`self.output_name`两个实例属性。
- `__call__`方法用于执行具体的功能，此处`_get_binary`用于完成二值化方法。
- `self.name`代表模块的名称，不要与其他模块重名。
- `self.output_name`代表模块输出的名称，将储存于一个共享的字典中。

当我们实例化SuperCCM并且进行调用时:

```python
from superccm import SuperCCM
from superccm.workflow import default_modules, default_workflow

superccm = SuperCCM(
    modules=default_modules,
    workflow=default_workflow,
)
file_path = 'your/img/path'
rst = superccm.run(file_path)
```

此时，superccm.run接收的参数将会原封不动的传递给workflow，
然后得到了其返回的具体的dict对象，用于指明每个模块所接收的输入。

SuperCCM顺序执行modules中的模块，并从workflow中获取其输入，

```python
class ReadImageModule(BaseModule):
    """
    A module for reading images, supporting multiple input types (file paths, URLs, numpy arrays, PIL images, etc.),
    and finally returning in the numpy array format of OpenCV.
    """

    def __init__(self):
        super().__init__()
        self.name = 'read'
        self.output_name = 'raw_image'

    def __call__(self, *args, **kwargs) -> np.ndarray:
        if not args:
            raise ValueError("An input is required.")
        return _read_image(*args, **kwargs)
```

例如对于第一个`ReadImageModule`来说，其`self.name`为`read`，
其输入为:`(img, 'gray')`
`img`是动态的，由刚刚传入的参数决定，`gray`则为设定的缺省值。

由于`self.output_name`为`raw_image`，其输出将被储存在`superccm.data['raw_image']`。

来到下一个模块`SegmentModule`，它需要获取到上一步读入的原始图像，所以在workflow中写作`[Data]raw_image`。

SuperCCM会特殊识别以`[Data]`开头的字符串，将其转为`superccm.data`中储存的值而非字符串本身。

> 以上介绍了SuperCCM的基本工作原理。
> 
> 没有看懂？让我们来看两个具体的例子。

## 例子1: 改进二值化方法

假如你开发了一种新颖的CCM图像二值化算法或模型，并且想要集成到SuperCCM中。

你将此算法包装为`sota_ccm_segment`方法:

```python
import numpy as np


def sota_ccm_segment(image: np.ndarray) -> np.ndarray:
    pass
```

然后，你需要编写一个新的模块:

```python
from superccm.modules.base import BaseModule


class SOTASegmentModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.name = 'sota_segment'  # your module name 
        self.output_name = 'binary_image'

    def __call__(self, *args, **kwargs) -> np.ndarray:
        if not args:
            raise ValueError("An input is required.")
        return sota_ccm_segment(*args, **kwargs)
```

此后，更新模块列表和工作流程:

```python
from typing import Any
from superccm.modules import (
    ReadImageModule, SkeletonizeModule, GraphifyModule, MetricsModule
)

your_modules = [
    ReadImageModule,
    SOTASegmentModule,  # your module
    SkeletonizeModule,
    GraphifyModule,
    MetricsModule,
]


def your_workflow(img) -> dict[str, tuple[Any]]:
    return {
        'read': (img, 'gray'),
        'sota_segment': ('[Data]raw_image',),  # update your module name
        'skeletonize': ('[Data]binary_image',),
        'graphify': ('[Data]raw_image', '[Data]binary_image', '[Data]skeleton_image'),
        'metrics': ('[Data]nerve_graph',),
    }
```

就可以正常使用了。
```python
from superccm import SuperCCM

superccm = SuperCCM(
    modules=your_modules,
    workflow=your_workflow,
)
file_path = 'your/img/path'
rst = superccm.run(file_path)
```


## 例子2: 增加一个预处理模块

假如你开发了一种新颖的CCM图像预处理算法，它可以改善CCM图像质量，并增强后续的分析效能。

你将此算法包装为`ccm_preprocess`方法:

```python
import numpy as np


def ccm_preprocess(image: np.ndarray) -> np.ndarray:
    pass
```

然后，你需要编写一个新的模块:

```python
from superccm.modules.base import BaseModule


class PreprocessModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.name = 'preprocess'  # your module name 
        self.output_name = 'preprocessed_image'

    def __call__(self, *args, **kwargs) -> np.ndarray:
        if not args:
            raise ValueError("An input is required.")
        return ccm_preprocess(*args, **kwargs)
```

此后，更新模块列表和工作流程:

```python
from typing import Any
from superccm.modules import (
    ReadImageModule, SegmentModule, SkeletonizeModule, GraphifyModule, MetricsModule
)
from your_pyscript import PreprocessModule

default_modules = [
    ReadImageModule,
    PreprocessModule,  # your module
    SegmentModule,
    SkeletonizeModule,
    GraphifyModule,
    MetricsModule,
]


def default_workflow(img) -> dict[str, tuple[Any]]:
    return {
        'read': (img, 'gray'),
        'preprocess': ('[Data]raw_image',),  # insert your module name
        'segment': ('[Data]preprocessed_image',),
        'skeletonize': ('[Data]binary_image',),
        'graphify': ('[Data]raw_image', '[Data]binary_image', '[Data]skeleton_image'),
        'metrics': ('[Data]nerve_graph',),
    }
```

就可以正常使用了。
```python
from superccm import SuperCCM

superccm = SuperCCM(
    modules=your_modules,
    workflow=your_workflow,
)
file_path = 'your/img/path'
rst = superccm.run(file_path)
```
