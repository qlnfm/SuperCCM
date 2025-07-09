# 可视化


1. 图像准备

准备一张[CCM角膜神经纤维图像](assets/auto_analysis/img.jpg)。

<img src="assets/vis/img.jpg" width="300">

2. 图像读取

使用合适的方法读取图像。
```python
import cv2
image = cv2.imread('assets/vis/img.jpg')
print(image.shape)
```
Output:
```text
(384, 384, 3)
```

3. 图像可视化

```python
from superccm import SuperCCM, draw

ccm = SuperCCM()
ccm(image)
draw(ccm.nerve_image, ccm.nerve_graph)
```
Output:

<img src="assets/vis/result.png" width="300">

