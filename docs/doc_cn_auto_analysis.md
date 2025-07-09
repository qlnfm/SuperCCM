# 自动分析


1. 图像准备

准备一张[CCM角膜神经纤维图像](assets/auto_analysis/img.jpg)。

<img src="assets/auto_analysis/img.jpg" width="300">

2. 图像读取

使用合适的方法读取图像。
```python
import cv2
image = cv2.imread('assets/auto_analysis/img.jpg')
print(image.shape)
```
Output:
```text
(384, 384, 3)
```

3. 图像分析

```python
from superccm import SuperCCM

ccm = SuperCCM()
metrics = ccm(image)
print(metrics)
```
Output:
```text
{'CNFL': 22.009, 'CNFD': 31.25, 'CNBD': 43.75, 'CNFA': 0.077, 'CNFW': 0.022, 'CTBD': 100.0, 'CNFT': 12.141, 'CNFrD': 1.428}
```