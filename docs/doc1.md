# 🎇SuperCCM Quick Tutorial

## Introduction

SuperCCM provides two usage styles: **functional** and **object-oriented**.

### Object-Oriented:

```python
from superccm import DefaultWorkFlow
from superccm.api import vis_ACCM, show_image

wf = DefaultWorkFlow()
metrics = wf.run('test.jpg')
print(metrics)
vis_img = vis_ACCM(wf.graph, wf.image)
show_image(vis_img)
```

### Functional:

```python
from superccm.api import analysis, analysis_and_vis, show_image

metrics = analysis('test.jpg')
print(metrics)
# Visualization
metrics, vis_img = analysis_and_vis('test.jpg')
show_image(vis_img)
```

## Reading Images

`SuperCCM.run` accepts multiple input formats, such as:

* **Local Path**

```python
from superccm import DefaultWorkFlow

wf = DefaultWorkFlow()
metrics = wf.run('your/img/path')
print(metrics)
```

* **np.ndarray**

```python
from superccm import DefaultWorkFlow
import cv2

img = cv2.imread('your/img/path', 0)
wf = DefaultWorkFlow()
metrics = wf.run(img)
print(metrics)
```

* **PIL.Image**

```python
from superccm import DefaultWorkFlow
from PIL import Image

img = Image.open('your/img/path')
wf = DefaultWorkFlow()
metrics = wf.run(img)
print(metrics)
```

* **URL**

```python
from superccm import DefaultWorkFlow

img_url = 'https://www.yourimgurl.com/your/img/url'
wf = DefaultWorkFlow()
metrics = wf.run(img_url)
print(metrics)
```
