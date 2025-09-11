# SuperCCM Custom Modules and Workflows

SuperCCM allows you to integrate your own algorithms into its workflow.

> If you don't want to do this yourself, please contact me at jugking6688@gmail.com. I will reply within 24 hours.

## Basic Knowledge: How Does SuperCCM Work?

SuperCCM executes tasks by sequentially concatenating modules and uses a workflow to control specific parameters. By default, the list of modules and the workflow are as follows:

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

For example, the `SegmentModule` is used to perform the image binarization task:

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

  - `SegmentModule` inherits from `BaseModule`, which is an abstract base class. It requires a module to have a `__call__` method and to define the `self.name` and `self.output_name` instance attributes.
  - The `__call__` method is used to perform the specific function; here, `_get_binary` is used to complete the binarization method.
  - `self.name` represents the module's name. It should not be the same as any other module.
  - `self.output_name` represents the name of the module's output, which will be stored in a shared dictionary.

When we instantiate and call SuperCCM:

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

At this point, the parameters received by `superccm.run` are passed directly to the workflow, which then returns a specific dictionary object to specify the input for each module.

SuperCCM executes the modules in the `modules` list sequentially and gets their input from the `workflow`.

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

For example, for the first `ReadImageModule`, its `self.name` is `read`, and its input is `(img, 'gray')`. `img` is dynamic and determined by the parameter just passed, while `gray` is the default value.

Since `self.output_name` is `raw_image`, its output will be stored in `superccm.data['raw_image']`.

Moving to the next module, `SegmentModule`, it needs to get the original image read in the previous step, so it is written as `'[Data]raw_image'` in the workflow.

SuperCCM specifically recognizes strings starting with `[Data]`, converting them to the value stored in `superccm.data` instead of the string itself.

> The above introduced the basic working principle of SuperCCM.
>
> Still not clear? Let's look at two specific examples.

## Example 1: Improving the Binarization Method

Suppose you have developed a new CCM image binarization algorithm or model and want to integrate it into SuperCCM.

You can wrap this algorithm in a `sota_ccm_segment` method:

```python
import numpy as np


def sota_ccm_segment(image: np.ndarray) -> np.ndarray:
    pass
```

Then, you need to write a new module:

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

Afterward, update the module list and workflow:

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

You can then use it normally.

```python
from superccm import SuperCCM

superccm = SuperCCM(
    modules=your_modules,
    workflow=your_workflow,
)
file_path = 'your/img/path'
rst = superccm.run(file_path)
```

## Example 2: Adding a Preprocessing Module

Suppose you have developed a new CCM image preprocessing algorithm that can improve CCM image quality and enhance the efficiency of subsequent analysis.

You can wrap this algorithm in a `ccm_preprocess` method:

```python
import numpy as np


def ccm_preprocess(image: np.ndarray) -> np.ndarray:
    pass
```

Then, you need to write a new module:

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

Afterward, update the module list and workflow:

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

You can then use it normally.

```python
from superccm import SuperCCM

superccm = SuperCCM(
    modules=your_modules,
    workflow=your_workflow,
)
file_path = 'your/img/path'
rst = superccm.run(file_path)
```